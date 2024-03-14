import React from 'react';
import { Collapse, Autocomplete, TextField, Box, Divider } from '@mui/material';
import FilterTitle from '../FilterTitle';

function QuerySpecificFilters({updatePage, name, filterType, expand, handleExpand, optionsAvailable}) {

    const updateFilter = (category ,value) => {
        updatePage("add", ["", category, value]);
    }

    return(
        <div>
            <FilterTitle name={`${name} (${optionsAvailable.length})`} expand={expand} handleExpand={handleExpand}/>
            <Divider/>
            <Collapse in={expand} timeout="auto" unmountOnExit style={{ height: "auto", overflow: "auto", backgroundColor: "#F5F5F5" }}>
                <Box sx={{ pt: 1.5, pb: 1.5, pr: "5%", pl: "5%" }}>
                    <Autocomplete disablePortal options={optionsAvailable} sx={{ width: "100%" }} onChange={(_, value) => {updateFilter(filterType, value);}} renderInput={(params) => <TextField {...params} label="Select" />}/>
                </Box>
            </Collapse>
            <Divider/>
        </div>
    )
}

export default QuerySpecificFilters;