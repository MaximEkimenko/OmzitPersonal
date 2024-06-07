import React, { useState, useEffect } from 'react'

const DateRangeSelector = ({ onApplyDateRange }) => {
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')

    useEffect(() => {
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 2)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1)

        setStartDate(firstDayOfMonth.toISOString().split('T')[0])
        setEndDate(lastDayOfMonth.toISOString().split('T')[0])
    }, [])

    const handleStartDateChange = (event) => {
        setStartDate(event.target.value)
    }

    const handleEndDateChange = (event) => {
        setEndDate(event.target.value)
    }

    const handleApply = () => {
        onApplyDateRange(startDate, endDate)
    }

    return (
        <div className='date-range-selector'>
            <input type='date' value={startDate} onChange={handleStartDateChange} />
            <input type='date' value={endDate} onChange={handleEndDateChange} />
            <button onClick={handleApply}>Применить</button>
        </div>
    )
}

export default DateRangeSelector
