import React, { useRef, useMemo, useImperativeHandle, forwardRef, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import './CustomGrid.css' // Импортируем CSS
import { AG_GRID_LOCALE_RU } from '../locale/locale'

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

        const handleFillNightShift = () => {
            if (!selectedCell) return

            const dayValue = parseFloat(prompt('Табель ДЕНЬ (не более 12)'))
            const nightValue = parseFloat(prompt('Табель НОЧЬ (не более 12)'))

            if (isNaN(dayValue) || isNaN(nightValue)) {
                alert('Некорректный ввод. Пожалуйста, введите числовое значение.')
                return
            }

            if (dayValue <= 0 || nightValue <= 0 || dayValue > 12 || nightValue > 12) {
                alert('Некорректный ввод. Числа должны быть положительными и не более 12.')
                return
            }

            const displayValue = `Д${dayValue}|Н${nightValue}`
            selectedCell.data[selectedCell.colDef.field] = displayValue

            // Обновляем таблицу
            selectedCell.api.refreshCells({
                columns: [selectedCell.colDef.field],
                rowNodes: [selectedCell.node],
            })
        }

        return (
            <div className='ag-theme-alpine' style={{ height: 700, width: '100%' }}>
                <button className='night-btn' onClick={handleFillNightShift}>
                    Заполнить ночные
                </button>
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
                    onCellClicked={handleCellClick}
                />
            </div>
        )
    }
)

export default CustomGrid
