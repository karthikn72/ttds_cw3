import React from 'react';
import { Search, Tune } from '@mui/icons-material';
import { IconButton, Tooltip } from '@mui/material';

function SearchBar({query, setQuery, submitQuery, viewFilters}) {

    return(
        <form className='search-box' onSubmit={submitQuery} style={{ width: "100%" }}>
            <div className='icon-segment'>
                <Search className='icon'/>
                <input type='search' placeholder='Search news articles' value={query} onChange={(event) => setQuery(event.target.value)}/>
                
                <Tooltip title="Apply Filters">
                    <IconButton  style={{ right: "15px"}} className='icon-right' color='primary' onClick={viewFilters}>
                        <Tune color='primary'/>
                    </IconButton>
                </Tooltip>

                <div className='icon-right divider' style={{ right: "65px" }}/>
            </div>
        </form>       
    )
}

export default SearchBar; 