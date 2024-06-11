import React, { useRef, useMemo, useImperativeHandle, forwardRef, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import './CustomGrid.css' // Импортируем CSS
import { AG_GRID_LOCALE_RU } from '../locale/locale'
// import { ModuleRegistry } from '@ag-grid-community/core'
// ModuleRegistry.registerModules([MenuModule])

const CustomGrid = forwardRef(
    ({ rowData, columnDefs, onCellValueChanged, onCellDoubleClicked }, ref) => {
        const gridRef = useRef()
        const localeText = useMemo(() => AG_GRID_LOCALE_RU, [])

        useImperativeHandle(ref, () => ({
            api: gridRef.current.api,
            columnApi: gridRef.current.columnApi,
            ensureColumnVisible: (field) => {
                if (gridRef.current.api) {
                    gridRef.current.api.ensureColumnVisible(field)
                }
            },
        }))

        const autoSizeStrategy = {
            type: 'fitCellContents',
            defaultMinWidth: 100,
        }

        const [selectedCell, setSelectedCell] = useState(null)

        const handleCellClick = (params) => {
            setSelectedCell(params)
        }

        const handleFillNightShift = (params) => {
            if (!params.data) return

            const dayValue = parseFloat(prompt('Введите значение для дня (не более 12)'))
            const nightValue = parseFloat(prompt('Введите значение для ночи (не более 12)'))

            if (isNaN(dayValue) || isNaN(nightValue)) {
                alert('Некорректный ввод. Пожалуйста, введите числовое значение.')
                return
            }

            if (dayValue <= 0 || nightValue <= 0 || dayValue > 12 || nightValue > 12) {
                alert('Некорректный ввод. Числа должны быть положительными и не более 12.')
                return
            }

            const displayValue = `${dayValue}/${nightValue}`
            params.data[params.colDef.field] = displayValue
            params.data.skud_day_duration[params.colDef.field] = {
                day: dayValue,
                night: nightValue,
            }

            // Обновляем таблицу
            params.api.refreshCells({
                columns: [params.colDef.field],
                rowNodes: [params.node],
            })
        }

        return (
            <div className='ag-theme-alpine' style={{ height: 600, width: '100%' }}>
                <AgGridReact
                    ref={gridRef}
                    rowData={rowData}
                    columnDefs={columnDefs}
                    defaultColDef={{ sortable: true, filter: true, resizable: true }}
                    onCellValueChanged={onCellValueChanged}
                    autoSizeStrategy={autoSizeStrategy}
                    columnHoverHighlight={true}
                    localeText={localeText}
                    onCellDoubleClicked={onCellDoubleClicked}
                />
            </div>
        )
    }
)

export default CustomGrid
