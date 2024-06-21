import React, { useState, useEffect, useRef, useImperativeHandle } from 'react'
import CustomGrid from './components/CustomGrid'
import ToggleButtons from './components/ToggleButtons'
import SaveButton from './components/SaveButton'
import DivisionSelector from './components/DivisionSelector'
import DateRangeSelector from './components/DateRangeSelector'
import Notification from './Notification.js'
import './App.css'
import { fetchDataFromAPI } from './services/apiService'
import {
    getDaysInMonth,
    getTodayDate,
    getDatesBeforeToday,
    getDatesAfterToday,
} from './utils/dateUtils'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import EmployeeDetails from './components/EmployeeDetails'
import CompanyRenderer from './companyRenderer.jsx'
import Button1CJson from './components/Button1CJson.js'

const isWeekend = (dateString) => {
    const date = new Date(dateString)
    const day = date.getDay()
    return day === 0 || day === 6 // Sunday or Saturday
}

const today = new Date()

const App = () => {
    const [rowData, setRowData] = useState([])
    const [columnDefs, setColumnDefs] = useState([])
    const [originalData, setOriginalData] = useState([])
    const [hiddenColumns, setHiddenColumns] = useState(['division', 'jobTitle'])
    const [selectedDivision, setSelectedDivision] = useState('')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [isLateView, setIsLateView] = useState(false)
    const [notification, setNotification] = useState({ message: '', type: '' })
    const [isModified, setIsModified] = useState(false)
    const gridRef = useRef()

    useEffect(() => {
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 2)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1)
        setStartDate(firstDayOfMonth.toISOString().split('T')[0])
        setEndDate(lastDayOfMonth.toISOString().split('T')[0])
    }, [])

    // const baseUrl = 'http://192.168.8.163:8005'
    const baseUrl = 'http://192.168.8.163:5001'

    useEffect(() => {
        const fetchData = async () => {
            if (!startDate || !endDate) {
                return
            }
            // const url = selectedDivision
            //     ? `${baseUrl}/e/timesheet?division=${selectedDivision}&start_time=${startDate}&end_time=${endDate}`
            //     : `${baseUrl}/e/timesheet?division=&start_time=${startDate}&end_time=${endDate}`
            // const data = await fetchDataFromAPI(url)
            console.log(selectedDivision)
            const url = selectedDivision
                ? `${baseUrl}/e/responsible_timesheet?fio_responsible=${selectedDivision}&start_time=${startDate}&end_time=${endDate}`
                : `${baseUrl}/e/responsible_timesheet?fio_responsible=&start_time=${startDate}&end_time=${endDate}`
            const data = await fetchDataFromAPI(url)
            console.log(url)

            setOriginalData(data)

            const transformedData = transformData(data, isLateView)
            setRowData(transformedData.rowData)
            setColumnDefs(transformedData.columnDefs)
        }
        fetchData()
    }, [selectedDivision, startDate, endDate, isLateView])

    const transformData = (data, isLate) => {
        const employees = {}
        const dates = getDaysInMonth(startDate, endDate)
        data.forEach((item) => {
            const fio_id = item.employee.id
            // const skud_night_duration = item.skud_night_duration
            // console.log(skud_night_duration)
            // const kvl = item.employee.KVL
            const fio = item.employee.fio
            const division = item.employee.division
            const jobTitle = item.employee.job_title
            const date = item.date.split('T')[0]
            const value = isLate ? item.late_value : item.skud_day_duration
            const dayStatus = item.day_status_short
            if (!employees[fio]) {
                employees[fio] = { division, jobTitle, fio_id }
            }
            employees[fio][date] = {
                skud_day_duration: String(value),
                day_status: dayStatus,
                fio_id: fio_id,
                late_value: item.late_value,
                kvl: item.employee.KVL,
                skud_night_duration: item.skud_night_duration,
            }
        })

        const rowData = Object.keys(employees).map((fio) => {
            const row = {
                fio_id: employees[fio].fio_id,
                fio,
                kvl: employees[fio].kvl,
                division: employees[fio].division,
                jobTitle: employees[fio].jobTitle,
            }
            let sum = 0
            dates.forEach((date) => {
                const dayData = employees[fio][date] || {}
                // prettier-ignore
                const value = 
                !dayData.skud_night_duration // если нет ночных
                    ? (dayData.day_status && dayData.day_status !== 'Я'  // если не явка 
                        ? dayData.day_status  // заполняем буквенный статус
                        : dayData.skud_day_duration || '') // заполняем скуд дня
                    : `Д${dayData.skud_day_duration}|Н${dayData.skud_night_duration}` // заполняем скуд с ночью
                row[date] = value

                const numericValue = parseFloat(dayData.skud_day_duration)
                if (!isNaN(numericValue)) {
                    sum += numericValue
                }
            })
            row['sum'] = sum.toFixed(1)
            return row
        })

        const columnDefs = [
            {
                headerName: 'ФИО',
                field: 'fio',
                editable: false,
                pinned: 'left',
                lockPosition: true,
                cellStyle: { textAlign: 'center' },
                cellRenderer: CompanyRenderer,
            },
            {
                headerName: 'Подразделение',
                field: 'division',
                editable: false,
                hide: hiddenColumns.includes('division'),
                cellStyle: { textAlign: 'center' },
            },
            {
                headerName: 'Должность',
                field: 'jobTitle',
                editable: false,
                hide: hiddenColumns.includes('jobTitle'),
                cellStyle: { textAlign: 'center' },
            },
            ...dates.map((date) => ({
                headerName: formatDate(date),
                width: 95,
                field: date,
                editable: true,
                hide: hiddenColumns.includes(date),

                cellClassRules: {
                    'red-flag': (params) => Number(params.value) < 8 && !isLateView,
                    'green-flag': (params) => Number(params.value) >= 8 && !isLateView,
                    'red-late-flag': (params) => Number(params.value) > 0 && isLateView,
                    'green-late-flag': (params) => Number(params.value) === 0 && isLateView,
                    'green-absent-flag': (params) =>
                        ['А', 'Б', 'В', 'К', 'О'].includes(params.value),
                    'weekend-flag': (params) => isWeekend(params.colDef.field),
                    'today-flag': (params) =>
                        params.colDef.field === today.toISOString().split('T')[0],
                    'night-flag': (params) => params.value.includes('|'),
                },
                cellStyle: { textAlign: 'center', fontSize: '20px', fontWeight: 'bold' },
                cellEditor: 'agSelectCellEditor',
                cellEditorParams: {
                    // prettier-ignore
                    // values: ['0', '0.5', '1','1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9',
                    //     '9.5', '10', '10.5', '11', '11.5', '12', '12.5', '13', '13.5', '14',
                    //     'А', 'Б', 'В', 'О', 'К',
                    // ],
                    values: ['','0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',  '11',  '12',  '13',  '14', 
                        'А', 'Б', 'В', 'О', 'К',
                    ],
                },
            })),
            {
                headerName: 'Итого',
                width: 105,
                field: 'sum',
                editable: false,
                cellStyle: { textAlign: 'center', fontSize: '20px', fontWeight: 'bold' },
                pinned: 'right',
                lockPinned: true,
                lockPosition: true,
            },
        ]
        return { rowData, columnDefs }
    }

    const formatDate = (date) => {
        const [year, month, day] = date.split('-')
        return `${day}.${month}`
    }

    const onCellValueChanged = (params) => {
        setIsModified(true)
        const updatedRowData = rowData.map((row) => {
            if (row.fio === params.data.fio) {
                const updatedRow = { ...row, [params.colDef.field]: params.newValue }
                let sum = 0
                Object.keys(updatedRow).forEach((key) => {
                    if (
                        key !== 'fio' &&
                        key !== 'division' &&
                        key !== 'jobTitle' &&
                        key !== 'sum'
                    ) {
                        const numericValue = parseFloat(updatedRow[key])
                        if (!isNaN(numericValue)) {
                            sum += numericValue
                        }
                    }
                })
                updatedRow['sum'] = sum.toFixed(1)
                return updatedRow
            }
            return row
        })
        setRowData(updatedRowData)
    }
    const handleSave = async () => {
        try {
            const updatedData = rowData.map((row) => {
                const employeeData = originalData.find((item) => item.employee.fio === row.fio)
                const updatedEmployeeData = {
                    ...employeeData,
                    skud_day_duration: { ...employeeData.skud_day_duration },
                    day_status: employeeData.day_status,
                }

                Object.keys(row).forEach((key) => {
                    if (
                        key !== 'fio' &&
                        key !== 'division' &&
                        key !== 'jobTitle' &&
                        key !== 'sum' &&
                        key !== 'fio_id'
                    ) {
                        updatedEmployeeData.skud_day_duration[key] = row[key]
                    } else if (key === 'division') {
                        updatedEmployeeData.employee.division = row[key]
                    } else if (key === 'jobTitle') {
                        updatedEmployeeData.employee.job_title = row[key]
                    }
                })
                // console.log(updatedEmployeeData)
                return updatedEmployeeData
            })

            const response = await fetch(`${baseUrl}/e/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData),
            })
            if (!response.ok) {
                throw new Error('Failed to save data')
            }
            setNotification({ message: 'Сохранено успешно', type: 'success' })
            setTimeout(() => setNotification({ message: '', type: '' }), 3000)
            console.log('Data saved successfully')
        } catch (error) {
            setNotification({ message: 'Ошибка сохранения', type: 'error' })
            setTimeout(() => setNotification({ message: '', type: '' }), 3000)
            console.error('Error saving data', error)
        }
    }

    const toggleColumn = (field) => {
        setHiddenColumns((prevHiddenColumns) =>
            prevHiddenColumns.includes(field)
                ? prevHiddenColumns.filter((col) => col !== field)
                : [...prevHiddenColumns, field]
        )
    }

    const toggleColumnsBeforeToday = () => {
        const datesBeforeToday = getDatesBeforeToday()
        setHiddenColumns((prevHiddenColumns) =>
            datesBeforeToday.every((date) => prevHiddenColumns.includes(date))
                ? prevHiddenColumns.filter((col) => !datesBeforeToday.includes(col))
                : [...new Set([...prevHiddenColumns, ...datesBeforeToday])]
        )
    }

    const toggleColumnsAfterToday = () => {
        const datesAfterToday = getDatesAfterToday()
        setHiddenColumns((prevHiddenColumns) =>
            datesAfterToday.every((date) => prevHiddenColumns.includes(date))
                ? prevHiddenColumns.filter((col) => !datesAfterToday.includes(col))
                : [...new Set([...prevHiddenColumns, ...datesAfterToday])]
        )
    }

    const focusTodayColumn = () => {
        const today = getTodayDate()
        if (gridRef.current) {
            gridRef.current.ensureColumnVisible(today)
        }
    }

    useEffect(() => {
        if (originalData.length > 0) {
            const transformedData = transformData(originalData, isLateView)
            setRowData(transformedData.rowData)
            setColumnDefs(transformedData.columnDefs)
        }
    }, [hiddenColumns])

    return (
        <Router>
            <div className='app-container'>
                <Notification message={notification.message} type={notification.type} />
                <Routes>
                    <Route
                        path='/'
                        element={
                            <>
                                <ToggleButtons
                                    toggleColumn={toggleColumn}
                                    toggleColumnsBeforeToday={toggleColumnsBeforeToday}
                                    toggleColumnsAfterToday={toggleColumnsAfterToday}
                                    focusTodayColumn={focusTodayColumn}
                                    isLateView={isLateView}
                                    setIsLateView={setIsLateView}
                                />
                                <h1>
                                    {isLateView
                                        ? `Опоздания отвественного: ${selectedDivision}`
                                        : `Табель ответственного: ${selectedDivision}`}
                                </h1>
                                <div className='control-panel'>
                                    {isModified && <SaveButton handleSave={handleSave} />}
                                    <DivisionSelector
                                        onSelectDivision={setSelectedDivision}
                                        baseUrl={baseUrl}
                                    />
                                    <DateRangeSelector
                                        onApplyDateRange={(start, end) => {
                                            setStartDate(start)
                                            setEndDate(end)
                                        }}
                                    />
                                </div>

                                <CustomGrid
                                    ref={gridRef}
                                    rowData={rowData}
                                    columnDefs={columnDefs}
                                    onCellValueChanged={onCellValueChanged}
                                />
                                {/* <Button1CJson baseUrl={baseUrl}></Button1CJson> */}
                            </>
                        }
                    />

                    {/* {console.log(selectedDivision)} */}
                    <Route path='/employee/:fio' element={<EmployeeDetails baseUrl={baseUrl} />} />
                </Routes>
            </div>
        </Router>
    )
}

export default App
// HOST=0.0.0.0 npm run start
