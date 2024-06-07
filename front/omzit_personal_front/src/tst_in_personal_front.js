import React, { useCallback, useMemo, useRef, useState, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AgGridReact } from '@ag-grid-community/react'
import '@ag-grid-community/styles/ag-grid.css'
import '@ag-grid-community/styles/ag-theme-quartz.css'
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model'
import { ClipboardModule } from '@ag-grid-enterprise/clipboard'
import { ExcelExportModule } from '@ag-grid-enterprise/excel-export'
import { MenuModule } from '@ag-grid-enterprise/menu'
import { RangeSelectionModule } from '@ag-grid-enterprise/range-selection'
import { RowGroupingModule } from '@ag-grid-enterprise/row-grouping'
import { SetFilterModule } from '@ag-grid-enterprise/set-filter'
import { MenuModule } from '@ag-grid-enterprise/menu'
import { ModuleRegistry } from '@ag-grid-community/core'
ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    ClipboardModule,
    ExcelExportModule,
    MenuModule,
    RangeSelectionModule,
    RowGroupingModule,
    SetFilterModule,
])

const GridExample = () => {
    const containerStyle = useMemo(() => ({ width: '100%', height: '100%' }), [])
    const gridStyle = useMemo(() => ({ height: '100%', width: '100%' }), [])
    const [rowData, setRowData] = useState()
    const [columnDefs, setColumnDefs] = useState([
        { field: 'athlete' },
        { field: 'age', minWidth: 100 },
        { field: 'hasGold', minWidth: 100, headerName: 'Gold' },
        {
            field: 'hasSilver',
            minWidth: 100,
            headerName: 'Silver',
            cellRendererParams: { disabled: true },
        },
        { field: 'dateObject', headerName: 'Date' },
        { field: 'date', headerName: 'Date (String)' },
        { field: 'countryObject', headerName: 'Country' },
    ])
    const defaultColDef = useMemo(() => {
        return {
            flex: 1,
            minWidth: 180,
            filter: true,
            floatingFilter: true,
            editable: true,
            enableRowGroup: true,
        }
    }, [])
    const dataTypeDefinitions = useMemo(() => {
        return {
            object: {
                baseDataType: 'object',
                extendsDataType: 'object',
                valueParser: (params) => ({ name: params.newValue }),
                valueFormatter: (params) => (params.value == null ? '' : params.value.name),
            },
        }
    }, [])

    const onGridReady = useCallback((params) => {
        fetch('https://www.ag-grid.com/example-assets/olympic-winners.json')
            .then((resp) => resp.json())
            .then((data) =>
                setRowData(
                    data.map((rowData) => {
                        const dateParts = rowData.date.split('/')
                        return {
                            ...rowData,
                            date: `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`,
                            dateObject: new Date(
                                parseInt(dateParts[2]),
                                parseInt(dateParts[1]) - 1,
                                parseInt(dateParts[0])
                            ),
                            countryObject: {
                                name: rowData.country,
                            },
                            hasGold: rowData.gold > 0,
                            hasSilver: rowData.silver > 0,
                        }
                    })
                )
            )
    }, [])

    return (
        <div style={containerStyle}>
            <div style={gridStyle} className={'ag-theme-quartz'}>
                <AgGridReact
                    rowData={rowData}
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    dataTypeDefinitions={dataTypeDefinitions}
                    enableFillHandle={true}
                    enableRangeSelection={true}
                    rowGroupPanelShow={'always'}
                    onGridReady={onGridReady}
                />
            </div>
        </div>
    )
}

const root = createRoot(document.getElementById('root'))
root.render(
    <StrictMode>
        <GridExample />
    </StrictMode>
)
window.tearDownExample = () => root.unmount()
