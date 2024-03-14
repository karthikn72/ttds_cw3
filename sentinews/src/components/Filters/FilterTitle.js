import React from 'react';
import { ExpandMoreSharp, ExpandLessSharp } from '@mui/icons-material';
import { IconButton } from '@mui/material';

function FilterTitle({name, expand, handleExpand}) {
    return(
        <div className='icon-segment' style={{ height: "60px" }}>
            <h6 className='filter-title'>{name}</h6>
            <IconButton onClick={handleExpand} className='filter-icon'>
                { expand ? <ExpandLessSharp/> : <ExpandMoreSharp/> }
            </IconButton>
        </div>
    )
}

export default FilterTitle;