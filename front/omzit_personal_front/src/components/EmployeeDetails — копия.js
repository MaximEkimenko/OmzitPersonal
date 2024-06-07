import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import CustomGrid from './CustomGrid'
import Notification from '../Notification'
import { fetchDataFromAPI } from '../services/apiService'
import './EmployeeDetails.css'
import '../App.css'

const EmployeeDetails = ({ baseUrl }) => {
    const { fio } = useParams()
    const [employeeData, setEmployeeData] = useState([])
    const [columnDefs, setColumnDefs] = useState([])
    const [notification, setNotification] = useState({ message: '', type: '' })
    const gridRef = useRef()
    const [orignDataFio, setOrignDataFio] = useState()
    useEffect(() => {
        const fetchEmployeeData = async () => {
            try {
                const data = await fetchDataFromAPI(`${baseUrl}/e/get_employee/${fio}`)
                setOrignDataFio(data.fio)
                // editor настройка выпадаюищх списков полей, для передачи
                const cellEditorSelector = (params) => {
                    if (params.data.type === 'division') {
                        return {
                            component: 'agSelectCellEditor',
                            params: {
                                values: [
                                    'цех №1',
                                    'цех №2',
                                    'цех №3',
                                    'цех №4',
                                    'УМК Участок малогабаритных конструкций',
                                ],
                                valueListGap: 5,
                            },
                            popup: true,
                        }
                    }
                    if (params.data.type === 'schedule') {
                        return {
                            component: 'agSelectCellEditor',
                            params: {
                                values: ['5/2', '2/2'],
                                valueListGap: 5,
                            },
                            popup: true,
                        }
                    }
                    return undefined
                }
                // колонки
                const columns = [
                    { headerName: 'Поле', field: 'field', editable: false },
                    {
                        headerName: 'Значение',
                        field: 'value',
                        editable: (params) => params.node.id == 2 || params.node.id == 3,
                        cellEditorSelector: cellEditorSelector,
                    },
                ]
                // значения
                const filteredData = [
                    { field: 'ФИО', value: data.fio },
                    { field: 'Должность', value: data.job_title },
                    {
                        field: 'Подразделение',
                        value: data.division,
                        type: 'division',
                    },
                    { field: 'График', value: data.schedule, type: 'schedule' },
                    {
                        field: 'Дата приёма',
                        value: new Date(Date.parse(data.employment_date)).toLocaleString('ru-Ru', {
                            year: 'numeric',
                            month: 'numeric',
                            day: 'numeric',
                        }),
                    },
                    { field: 'КВЛ', value: data.KVL },
                ]
                setEmployeeData(filteredData)
                setColumnDefs(columns)
            } catch (error) {
                console.error('Error fetching employee data:', error)
            }
        }
        fetchEmployeeData()
    }, [fio, baseUrl])
    const handleSave = async () => {
        try {
            const updatedEmployeeData = {}
            gridRef.current.api.forEachNode((node) => {
                const keyMap = {
                    'ФИО': 'fio',
                    'Должность': 'job_title',
                    'Подразделение': 'division',
                    'График': 'schedule',
                    'Категория КТР': 'KTR_category',
                    'КТР': 'KTR',
                    'Есть НАКС': 'has_NAX',
                    'Коэффциент НАКС': 'KNAX',
                }
                updatedEmployeeData[keyMap[node.data.field]] = node.data.value
            })
            const response = await fetch(`${baseUrl}/e/save_employee`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedEmployeeData),
            })
            if (!response.ok) {
                throw new Error('Failed to save employee data')
            }
            setNotification({ message: 'Employee data saved successfully', type: 'success' })
            setTimeout(() => setNotification({ message: '', type: '' }), 3000)
        } catch (error) {
            setNotification({ message: 'Error saving employee data', type: 'error' })
            setTimeout(() => setNotification({ message: '', type: '' }), 3000)
            console.error('Error saving employee data:', error)
        }
    }
    return (
        <div>
            <h1>{`${orignDataFio}`}</h1>
            <button type='button' onClick={handleSave}>
                Save
            </button>
            <a href={`/`}> назад </a>
            <Notification message={notification.message} type={notification.type} />
            <CustomGrid ref={gridRef} rowData={employeeData} columnDefs={columnDefs} />
            <button type='button' onClick={handleSave}>
                Save
            </button>
            {/* Кнопка для сохранения данных */}
        </div>
    )
}

export default EmployeeDetails
