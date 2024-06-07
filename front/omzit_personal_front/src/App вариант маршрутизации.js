import { BrowserRouter, Routes, Route } from 'react-router-dom'
import FioPage from './components/FioPage'
import TabelPage from './TabelPage'
import React, { useState, useEffect, useRef } from 'react'
import CustomGrid from './components/CustomGrid'
import ToggleButtons from './components/ToggleButtons'
import SaveButton from './components/SaveButton'
import DivisionSelector from './components/DivisionSelector'
import DateRangeSelector from './components/DateRangeSelector'
import Notification from './Notification'
import './App.css'
function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path='tabel' element={<TabelPage />} />
                <Route path='fio' element={<FioPage />} />
            </Routes>
        </BrowserRouter>
    )
}

//export default App
// HOST=0.0.0.0 npm run start
