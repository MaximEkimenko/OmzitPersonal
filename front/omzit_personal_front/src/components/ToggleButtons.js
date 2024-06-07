import React from 'react'
import './ToggleButtons.css'

const ToggleButtons = ({
    toggleColumn,
    toggleColumnsBeforeToday,
    toggleColumnsAfterToday,
    focusTodayColumn,
    handleSave,
    isLateView,
    setIsLateView,
}) => {
    const toggleLateView = () => {
        setIsLateView((prevIsLateView) => !prevIsLateView)
    }
    return (
        <div className='button-group'>
            <button className='toggle-button' onClick={() => toggleColumn('division')}>
                Скрыть/Показать подразделение
            </button>
            <button className='toggle-button' onClick={() => toggleColumn('jobTitle')}>
                Скрыть/Показать должность
            </button>
            {/* <button className='toggle-button' onClick={toggleColumnsBeforeToday}>
            Скрыть/Показать даты до сегодняшней
        </button>
        <button className='toggle-button' onClick={toggleColumnsAfterToday}>
            Скрыть/Показать даты после сегодняшней
        </button> */}
            <button className='toggle-button' onClick={focusTodayColumn}>
                Фокус на сегодня
            </button>
            <button onClick={toggleLateView} className='toggle-button'>
                {isLateView ? 'Показать табель' : 'Показать опоздания'}
            </button>
        </div>
    )
}
export default ToggleButtons
