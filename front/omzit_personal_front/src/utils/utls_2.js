export const getDaysInMonth = (
    year = new Date().getFullYear(),
    month = new Date().getMonth() + 1
) => {
    const date = new Date(year, month - 1, 1)
    const days = []
    while (date.getMonth() + 1 === month) {
        days.push(date.toISOString().split('T')[0])
        date.setDate(date.getDate() + 1)
    }
    return days
}

export const getTodayDate = () => new Date().toISOString().split('T')[0]

export const getDatesBeforeToday = () => {
    const today = getTodayDate()
    return getDaysInMonth().filter((date) => date < today)
}

export const getDatesAfterToday = () => {
    const today = getTodayDate()
    return getDaysInMonth().filter((date) => date > today)
}
