import React, { useState } from 'react'
import './Button1CJson.css'

const Button1CJson = ({ baseUrl }) => {
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState(null)

    const handleButtonClick = () => {
        if (!startDate || !endDate) {
            alert('Введите даты начала и конца')
            return
        }
        setLoading(true)
        fetch(`${baseUrl}/e/get1C?start_date=${startDate}&end_date=${endDate}`)
            .then((response) => response.json())
            .then((data) => {
                setData(data)
                setLoading(false)
                const json = JSON.stringify(data, null, 2)
                const blob = new Blob([json], { type: 'application/json' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'data.json'
                a.click()
            })
            .catch((error) => {
                console.error(error)
                setLoading(false)
            })
    }

    return (
        <div className='ButtonContainer'>
            <label className='Label'>Дата начала:</label>
            <input
                type='date'
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className='Input'
            />
            <label className='Label'>Дата конца:</label>
            <input
                type='date'
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className='Input'
            />
            <button className='Button' onClick={handleButtonClick}>
                Получить данные для 1С
            </button>
            {loading && <div className='Loading'>Загрузка...</div>}
        </div>
    )
}

export default Button1CJson
