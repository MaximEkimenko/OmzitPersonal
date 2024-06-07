import React from 'react'

export default (params) => {
    return (
        <a
            href={`http://192.168.8.163:3000/employee/${params.data.fio_id}/`}
            rel='noreferrer'
            target='_blank'
        >
            {params.data.fio}
        </a>
    )
}
