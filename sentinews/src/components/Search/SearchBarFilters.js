import React, { useState } from 'react';
import { Box, Grid, IconButton, Typography, TextField, Button, Divider } from '@mui/material';
import { Search, Close } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns/format';
import { getQueryType } from '../Helper';
import { toast } from 'react-toastify';
import BasicFilters from '../Filters/FilterCategories/BasicFilters';

function SearchBarFilters({handleClose, query, setQuery}) {

    const navigate = useNavigate();
    const [checked, setChecked] = useState([]);
    const [dateRange, setDateRange] = useState([{ startDate: null, endDate: new Date(), key: 'selection' }]);

    const formatDate = (dateString) => { return format(new Date(dateString), 'yyyy-MM-dd') };

    const submitFilterQuery = (e) => {
        e.preventDefault();

        const sanitisedQuery = query.trim();

        if (sanitisedQuery.length < 1) {
            return toast.error("Please provide a search query to continue.", { toastId: 'empty-query' });
        }

        setQuery(sanitisedQuery);
        let queryString = "/search?";
        const queryType = getQueryType(sanitisedQuery);
        const startDate = dateRange[0]?.startDate;
        const endDate = dateRange[0]?.endDate;

        queryString += `q=${query}&type=${queryType}`;
        queryString += checked.length > 0 ? `&sentiment=${checked}` : '';
        queryString += startDate && endDate ? `&from=${formatDate(startDate.toISOString())}&to=${formatDate(endDate.toISOString())}` : "";

        toast.dismiss();
        return navigate(queryString);
    }

    return(
        <div>
            <Box sx={{ m: 0.25 }}/>
            <Typography variant="h6" align="center">APPLY FILTERS</Typography>
            <IconButton style= {{ position: "absolute", top: "0", right: "0", margin: "10px"}} onClick={handleClose}>
                <Close/>
            </IconButton>

            <form onSubmit={submitFilterQuery}>
                <Grid container spacing={1}>
                    <Grid item xs={12} style={{ marginTop: "3%" }}>
                        <TextField type="search" label="Search news articles" variant="outlined" value={query} onChange={(event) => setQuery(event.target.value)} style={{ width: "100%" }}/>
                    </Grid>

                    <Grid item xs={12}>
                        <BasicFilters checked={checked} dateRange={dateRange} setChecked={setChecked} setDateRange={setDateRange}/>
                        <Divider style={{ marginTop: "-12px"}}/>
                    </Grid>

                    <Grid item xs={12} style={{ display: "flex", justifyContent: "center", flexDirection: "row", marginTop: "10px" }}>
                        <Button variant='contained' className='button-deco' type='submit' endIcon={<Search/>}>SEARCH</Button>
                    </Grid>
                </Grid>
            </form>
        </div>
    )
}

export default SearchBarFilters;