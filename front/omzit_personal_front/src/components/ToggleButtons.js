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
            <button className='toggle-button' onClick={focusTodayColumn}>
                Сегодня
            </button>
            <button className='toggle-button' onClick={() => toggleColumn('division')}>
                Подразделение
            </button>
            <button className='toggle-button' onClick={() => toggleColumn('jobTitle')}>
                Должность
            </button>
            {/* <button className='toggle-button' onClick={toggleColumnsBeforeToday}>
            Скрыть/Показать даты до сегодняшней
        </button>
        <button className='toggle-button' onClick={toggleColumnsAfterToday}>
            Скрыть/Показать даты после сегодняшней
        </button> */}

            <button onClick={toggleLateView} className='toggle-button'>
                {isLateView ? 'Табель' : 'Опоздания'}
            </button>
        </div>
    )
}
export default ToggleButtons
