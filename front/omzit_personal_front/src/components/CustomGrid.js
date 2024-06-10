import React, { useRef, useMemo, useImperativeHandle, forwardRef } from 'react'
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

        // useImperativeHandle(ref, () => ({
        //     ensureColumnVisible: (field) => {
        //         gridRef.current.api.ensureColumnVisible(field)
        //     },
        // }))

        const autoSizeStrategy = {
            type: 'fitCellContents',
            defaultMinWidth: 100,
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
