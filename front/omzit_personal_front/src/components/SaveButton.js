import React from 'react'
import './SaveButton.css'

const SaveButton = ({ handleSave }) => {
    return (
        <div className='save-button-container'>
            <button className='save-button' onClick={handleSave}>
                Сохранить изменения
            </button>
        </div>
    )
}

export default SaveButton
