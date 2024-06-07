// export const fetchDataFromAPI = async (url) => {
//     try {
//         const response = await fetch(url)
//         if (!response.ok) {
//             throw new Error('Failed to fetch data from API')
//         }
//         const data = await response.json()
//         return data
//     } catch (error) {
//         console.error('Error fetching data from API', error)
//         throw error
//     }
// }
export const fetchDataFromAPI = async (url) => {
    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error('Network response was not ok')
        }
        const data = await response.json()
        return data
    } catch (error) {
        console.error('Failed to fetch data:', error)
        return []
    }
}

export const fetchEmployeeDataFromAPI = async (url) => {
    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error('Network response was not ok')
        }
        const data = await response.json()
        return data
    } catch (error) {
        console.error('Failed to fetch employee data:', error)
        return {}
    }
}

export const saveEmployeeDataToAPI = async (url, data) => {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })

        if (!response.ok) {
            throw new Error('Failed to save data')
        }
        return response
    } catch (error) {
        console.error('Failed to save employee data:', error)
        return null
    }
}
