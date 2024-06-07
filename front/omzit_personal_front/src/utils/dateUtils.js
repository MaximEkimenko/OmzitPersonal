export const getDaysInMonth = (startDate, endDate) => {
    const dates = []
    const start = new Date(startDate)
    const end = new Date(endDate)

    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
        dates.push(date.toISOString().split('T')[0])
    }

    return dates
}
// export const getDaysInMonth = () => {
//     const now = new Date()
//     const year = now.getFullYear()
//     const month = now.getMonth()
//     const daysInMonth = new Date(year, month + 1, 0).getDate()
//     const dates = []
//     for (let day = 1; day <= daysInMonth; day++) {
//         const date = new Date(year, month, day + 1)
//         const dateString = date.toISOString().split('T')[0]
//         dates.push(dateString)
//     }
//     return dates
// }

export const getTodayDate = () => {
    const now = new Date()
    return now.toISOString().split('T')[0]
}

export const getDatesBeforeToday = () => {
    const today = getTodayDate()
    return getDaysInMonth().filter((date) => date < today)
}

export const getDatesAfterToday = () => {
    const today = getTodayDate()
    return getDaysInMonth().filter((date) => date > today)
}
