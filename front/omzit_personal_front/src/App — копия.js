import React, { useState, useEffect, useRef } from 'react'
import CustomGrid from './components/CustomGrid'
import ToggleButtons from './components/ToggleButtons'
import SaveButton from './components/SaveButton'
import DivisionSelector from './components/DivisionSelector'
import DateRangeSelector from './components/DateRangeSelector'
import './App.css'
import { fetchDataFromAPI } from './services/apiService'
import {
    getDaysInMonth,
    getTodayDate,
    getDatesBeforeToday,
    getDatesAfterToday,
} from './utils/dateUtils'

const App = () => {
    const [rowData, setRowData] = useState([])
    const [columnDefs, setColumnDefs] = useState([])
    const [originalData, setOriginalData] = useState([])
    const [hiddenColumns, setHiddenColumns] = useState([])
    const [selectedDivision, setSelectedDivision] = useState('')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const gridRef = useRef()

    useEffect(() => {
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 2)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1)
        // console.log(firstDayOfMonth, lastDayOfMonth)
        setStartDate(firstDayOfMonth.toISOString().split('T')[0])
        setEndDate(lastDayOfMonth.toISOString().split('T')[0])
    }, [])

    useEffect(() => {
        const fetchData = async () => {
            const baseUrl = 'http://192.168.8.163:7001'
            if (!startDate || !endDate) {
                return
            }
            // const url = `http://127.0.0.1:7001/e/timesheet?start_time=2024-05-01&end_time=2024-05-24`
            // const url = selectedDivision
            //     ? `http://127.0.0.1:7001/e/timesheet?division=${selectedDivision}&start_time=2024-05-01&end_time=2024-05-24`
            //     : 'http://127.0.0.1:7001/e/timesheet?start_time=2024-05-01&end_time=2024-05-24'
            const url = selectedDivision
                ? `${baseUrl}/e/timesheet?division=${selectedDivision}&start_time=${startDate}&end_time=${endDate}`
                : `${baseUrl}/e/timesheet?division=&start_time=${startDate}&end_time=${endDate}`
            const data = await fetchDataFromAPI(url)
            console.log(data)
            setOriginalData(data)
            const transformedData = transformData(data)
            setRowData(transformedData.rowData)
            setColumnDefs(transformedData.columnDefs)
        }

        fetchData()
    }, [selectedDivision, , startDate, endDate])

    const transformData = (data) => {
        const employees = {}
        // const dates = getDaysInMonth()
        const dates = getDaysInMonth(startDate, endDate)

        data.forEach((item) => {
            const fio = item.employee.fio
            const division = item.employee.division
            const jobTitle = item.employee.job_title
            // const lateValue = item.late_value
            const date = item.date.split('T')[0]

            // console.log(fio)

            if (!employees[fio]) {
                employees[fio] = { division, jobTitle }
                // employees[fio] = { division, jobTitle, lateValue }
            }
            // console.log(fio, item.skud_day_duration)

            employees[fio][date] = String(item.skud_day_duration)
            console.log(item.skud_day_duration)

            // employees[fio][date] = String(item.skud_day_duration)
        })

        const rowData = Object.keys(employees).map((fio) => {
            const row = {
                fio,
                division: employees[fio].division,
                jobTitle: employees[fio].jobTitle,
                // lateValue: employees[fio].lateValue,
            }
            let sum = 0 // Переменная для хранения суммы
            dates.forEach((date) => {
                const value = employees[fio][date] || ''
                row[date] = value

                // Если значение числовое, добавляем его к сумме
                const numericValue = parseFloat(value)
                if (!isNaN(numericValue)) {
                    sum += numericValue
                }
            })

            row['sum'] = sum.toFixed(1) // Устанавливаем значение суммы с одним знаком после запятой
            return row
        })

        const columnDefs = [
            {
                headerName: 'ФИО',
                field: 'fio',
                editable: true,
                pinned: 'left',
                cellStyle: { textAlign: 'center' },
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
                    'red-flag': (params) => Number(params.value) < 8,
                    'green-flag': (params) => Number(params.value) >= 8,
                },

                cellStyle: { textAlign: 'center', fontSize: '20px', fomtWeight: 'bold' },
                cellEditor: 'agSelectCellEditor',
                cellEditorParams: {
                    // prettier-ignore
                    values: ['0', '0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9',
                            '9.5', '10', '10.5', '11', '11.5', '12', '12.5', '13', '13.5', '14', 'А', 'Б', 'В', 'О', 'К', ],
                },
            })),

            // {
            //     headerName: 'late',
            //     width: 105,
            //     field: 'lateValue',
            //     editable: false,
            //     // cellStyle: { textAlign: 'center', fontSize: '20px', fontWeight: 'bold' },
            //     pinned: 'right',
            // },

            {
                headerName: 'Итого',
                width: 105,
                field: 'sum',
                editable: false,
                cellStyle: { textAlign: 'center', fontSize: '20px', fontWeight: 'bold' },
                pinned: 'right',
            },
        ]

        return { rowData, columnDefs }
    }

    const formatDate = (date) => {
        const [year, month, day] = date.split('-')
        return `${day}.${month}`
    }

    const onCellValueChanged = (params) => {
        const updatedRowData = rowData.map((row) => {
            if (row.fio === params.data.fio) {
                const updatedRow = { ...row, [params.colDef.field]: params.newValue }

                // Пересчитываем сумму для измененной строки
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
                    skud_day_duration: {},
                }

                Object.keys(row).forEach((key) => {
                    if (key !== 'fio' && key !== 'division' && key !== 'jobTitle') {
                        const dateKey = Object.keys(updatedEmployeeData).find((k) =>
                            k.includes(key)
                        )
                        if (dateKey) {
                            updatedEmployeeData.skud_day_duration[key] = row[key]
                        }
                    } else if (key === 'division') {
                        updatedEmployeeData.employee.division = row[key]
                    } else if (key === 'jobTitle') {
                        updatedEmployeeData.employee.job_title = row[key]
                    }
                })

                return updatedEmployeeData
            })

            const response = await fetch('https://api.example.com/data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData),
            })

            if (!response.ok) {
                throw new Error('Failed to save data')
            }

            console.log('Data saved successfully')
        } catch (error) {
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
            const transformedData = transformData(originalData)
            setRowData(transformedData.rowData)
            setColumnDefs(transformedData.columnDefs)
        }
    }, [hiddenColumns])

    return (
        <div className='app-container'>
            <h1 className='tabel-title'> Табель {selectedDivision} </h1>

            <div className='control-panel'>
                <SaveButton handleSave={handleSave} />
                <DivisionSelector onSelectDivision={setSelectedDivision} />
                <DateRangeSelector
                    onApplyDateRange={(start, end) => {
                        setStartDate(start)
                        setEndDate(end)
                    }}
                />
            </div>

            <ToggleButtons
                toggleColumn={toggleColumn}
                toggleColumnsBeforeToday={toggleColumnsBeforeToday}
                toggleColumnsAfterToday={toggleColumnsAfterToday}
                focusTodayColumn={focusTodayColumn}
            />
            <CustomGrid
                ref={gridRef}
                rowData={rowData}
                columnDefs={columnDefs}
                onCellValueChanged={onCellValueChanged}
            />
        </div>
    )
}

export default App
// HOST=0.0.0.0 npm run start
