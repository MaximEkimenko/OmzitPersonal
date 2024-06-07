import CustomGrid from './CustomGrid'
import React, { useState, useEffect, useRef } from 'react'
import { fetchDataFromAPI } from '../services/apiService'

const FioPage = (index) => {
    const baseUrl = 'http://192.168.8.163:8005'
    useEffect(() => {
        const fetchData = async () => {
            const url = `${baseUrl}/e/get_all_employees?amount=10`

            const data = await fetchDataFromAPI(url)

            console.log(data)
        }

        fetchData()
    }, [])

    return (
        <>
            <h3>База ФИО </h3>
            <a href='http://192.168.8.163:3000/tabel'> табель </a>

            <CustomGrid
            // ref={gridRef}
            // rowData={rowData}
            // columnDefs={columnDefs}
            // onCellValueChanged={onCellValueChanged}
            // onCellDoubleClicked={onCellDoubleClicked}
            />
        </>
    )
}
export default FioPage
