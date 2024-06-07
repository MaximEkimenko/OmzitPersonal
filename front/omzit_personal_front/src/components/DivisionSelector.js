import React, { useState, useEffect } from 'react'

const DivisionSelector = ({ onSelectDivision, baseUrl }) => {
    // const DivisionSelector = ({ selectedDivision, onDivisionChange }) => {
    const [divisions, setDivisions] = useState([])
    const [selectedDivision, setSelectedDivision] = useState()

    useEffect(() => {
        const fetchDivisions = async () => {
            try {
                const response = await fetch(`${baseUrl}/e/divisions`)
                if (!response.ok) {
                    throw new Error('Failed to fetch divisions')
                }
                const data = await response.json()
                setDivisions(data)
            } catch (error) {
                console.error('Error fetching divisions', error)
            }
        }
        fetchDivisions()
    }, [baseUrl])
    // console.log(divisions)
    // console.log(selectedDivision)
    const handleChange = (event) => {
        const division = event.target.value
        setSelectedDivision(division)
        onSelectDivision(division)
    }

    return (
        <div className='division-selector'>
            <select value={selectedDivision} onChange={handleChange}>
                <option value=''>Выберите подразделение</option>
                {divisions.map((division) => (
                    <option key={division.id} value={division.division}>
                        {division.division}
                    </option>
                ))}
            </select>
        </div>
    )
}

export default DivisionSelector
