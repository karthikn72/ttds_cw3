import React, { useState } from 'react';
import { Collapse, Box, Divider, Button } from '@mui/material';
import DateRangeIcon from '@mui/icons-material/DateRange';
import { DateRange } from 'react-date-range';
import { format } from 'date-fns/format';
import FilterTitle from '../FilterTitle';

function DateRangeSelector({updatePage, expand, handleExpand}) {

    const [state, setState] = useState([{
        startDate: new Date(),
        endDate: new Date(),
        key: 'selection'
    }]);

    const formatDate = (dateString) => { return format(new Date(dateString), 'yyyy-MM-dd') };

    const updateFilter = () => {
        const dateRange = state[0];
        const from = formatDate(dateRange.startDate.toISOString());
        const to = formatDate(dateRange.endDate.toISOString());
        updatePage("add", ["", "date", [from, to]]);
    }

    return(
        <div>
            <FilterTitle name={`DATE RANGE`} expand={expand} handleExpand={handleExpand}/>
            <Divider/>
            <Collapse in={expand} timeout="auto" unmountOnExit style={{ height: "auto", overflow: "auto", backgroundColor: "#F5F5F5" }}>
                <Box sx={{ justifyContent: "center", display: "flex" }}>
                    <DateRange showMonthAndYearPickers={true} style={{maxWidth: "285px" }} editableDateInputs={true} onChange={item => setState([item.selection])} ranges={state}/>
                </Box>

                <Box sx={{pt: 2, pb: 2, justifyContent: "center", display: "flex" }}>
                    <Button variant='contained' className='button-deco' startIcon={<DateRangeIcon/>} onClick={updateFilter}>APPLY</Button>
                </Box>
            </Collapse>
            <Divider/>
        </div>
    )
}

export default DateRangeSelector;