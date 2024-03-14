import React, { useState, useEffect } from 'react';
import { Box, Grid, IconButton, Typography, TextField, InputLabel, Stack, Button, Select, MenuItem, Autocomplete, FormControl, Divider, Collapse } from '@mui/material';
import { ExpandMore, ExpandLess, Search, Close } from '@mui/icons-material';
import { toast } from 'react-toastify';
import { format } from 'date-fns/format';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import BasicFilters from '../Filters/FilterCategories/BasicFilters';

function AdvancedSearch({handleClose}) {

    const navigate = useNavigate();

    const [gotPublications, setGotPublications] = useState(false);
    const [publicationsAvailable, setPublicationsAvailable] = useState([]);

    const [checked, setChecked] = useState([]);
    const [dateRange, setDateRange] = useState([{ startDate: null, endDate: new Date(), key: 'selection' }]);

    const [phraseQuery, setPhraseQuery] = useState("");
    const [booleanQuery1, setBooleanQuery1] = useState("");
    const [booleanOperator, setBooleanOperator] = useState("");
    const [booleanQuery2, setBooleanQuery2] = useState("");
    const [proximityTerm1, setProximityTerm1] = useState("");
    const [proximityTerm2, setProximityTerm2] = useState("");
    const [proximityDistance, setProximityDistance] = useState("");
    const [publicationQuery, setPublicationQuery] = useState("");
    const [openFilters, setOpenFilters] = useState(false);

    const handleFiltersToggle = () => setOpenFilters(state => !state);
    
    const formatDate = (dateString) => { return format(new Date(dateString), 'yyyy-MM-dd') };

    useEffect(() => {
        const retrievePublications = async () => {
            const endpointURL = `${process.env.REACT_APP_SENTINEWS_API_SERVER_URL}/unique_publications`;

            axios.get(endpointURL).then(response => {
                setPublicationsAvailable(response.data.unique_publications);
                setGotPublications(true);
            }).catch(error => { 
                if (error.response === undefined) {
                    toast.error("Our API server is not accepting requests at the moment. Please try again later!", { toastId: 'server-error-1' });
                } else {
                    const errorCode = error.response.status;

                    if (errorCode === 404) {
                        toast.error("Unable to retrieve publication list. Please try again later!", { toastId: 'publication-error' }); 
                    } else {
                        toast.error(`"We're experiencing an issue with our server at the moment. Please try again later! Error Code: ${errorCode}`, { toastId: 'server-error-2' }); 
                    }
                }
            });
        }

        retrievePublications();
    },[]);

    const submitAdvancedQuery = (e) => {
        e.preventDefault();

        const phraseData = { key: "Phrase", selected: phraseQuery.trim() };
        const booleanData = { key: "Boolean", selected: booleanQuery1 || booleanOperator || booleanQuery2 };
        const proximityData = { key: "Proximity", selected: proximityTerm1 || proximityTerm2 || proximityDistance };
        const publicationData = { key: "Publication", selected: publicationQuery };

        const queriesSelected = [phraseData, booleanData, proximityData, publicationData].filter(type => type.selected);

        if (queriesSelected.length === 0) {
            return toast.error("Please provide a search query to continue.", { toastId: 'no-queries-selected' });
        } else if (queriesSelected.length > 1) {
            return toast.error("Please use only one type of advanced search to continue.", { toastId: 'multiple-queries-selected' });
        } else {
            const queryType = queriesSelected[0].key;
            let queryString = "/search?q=";

            if (queryType === "Phrase") {
                queryString += `"${phraseQuery}"`;
            } else if (queryType === "Publication") {
                queryString += `Publication:${publicationQuery}`;
            } else if (queryType === "Boolean") {

                if (booleanQuery1.trim() && booleanOperator && booleanQuery2.trim()) {
                    queryString += `(${booleanQuery1},${booleanOperator},${booleanQuery2})`;
                } else {
                    return toast.error("Please complete the boolean query to continue.", { toastId: 'incomplete-boolean-query' });
                }

            } else if (queryType === "Proximity") {

                if (proximityTerm1.trim() && proximityTerm2.trim() && proximityDistance.trim()) {
                    queryString += `(${proximityTerm1},${proximityTerm2},${proximityDistance})`;
                } else {
                    return toast.error("Please complete the proximity query to continue.", { toastId: 'incomplete-proximity-query' });
                }

            }
            
            const startDate = dateRange[0]?.startDate;
            const endDate = dateRange[0]?.endDate;

            queryString += `&type=${queryType}`
            queryString += checked.length > 0 ? `&sentiment=${checked}` : '';
            queryString += startDate && endDate ? `&from=${formatDate(startDate.toISOString())}&to=${formatDate(endDate.toISOString())}` : "";

            toast.dismiss();
            return navigate(queryString);
        }
    }

    return(
        <div>
            <Box sx={{ m: 0.25 }}/>
            <Typography variant="h6" align="center">ADVANCED SEARCH OPTIONS</Typography>
            <IconButton style= {{ position: "absolute", top: "0", right: "0", margin: "10px"}} onClick={handleClose}>
                <Close/>
            </IconButton>

            <form onSubmit={submitAdvancedQuery}>
                <Grid container spacing={1}>

                    <Grid item xs={12} style={{ marginTop: "1%" }}>
                        <Typography variant="p" className='advanced-search-title'>PUBLICATION SEARCH</Typography>
                        <Autocomplete disabled={!gotPublications} options={publicationsAvailable} onChange={(_, value) => {setPublicationQuery(value);}} renderInput={(params) => <TextField {...params} label="Select a publication provider to query" />} style={{ width: "100%", marginTop: "1.5%" }}/>
                    </Grid>

                    <Grid item xs={12} style={{ marginTop: "3%" }}>
                        <Typography variant="p" className='advanced-search-title'>PHRASE SEARCH</Typography>
                        <TextField type="search" variant="outlined" label="Provide the exact word or phrase" value={phraseQuery} onChange={(event) => setPhraseQuery(event.target.value)} style={{ width: "100%", marginTop: "1.5%" }}/>
                    </Grid>

                    <Grid item xs={12} style={{ marginTop: "1%" }}>
                        <Typography variant="p" className='advanced-search-title'>BOOLEAN SEARCH</Typography>
                        
                        <Stack spacing={2} direction="row" style={{ marginTop: "1.5%" }}>
                            <TextField type="search" variant="outlined" label="Query 1" value={booleanQuery1} onChange={(event) => setBooleanQuery1(event.target.value)} style={{ flex: 1 }}/>
                            <FormControl style={{ flex: 1 }}>
                                <InputLabel id="operator-select">Operator</InputLabel>
                                <Select labelId='operator-select' value={booleanOperator} label="Operator" onChange={(event) => setBooleanOperator(event.target.value)}>
                                    <MenuItem value="AND">AND</MenuItem>
                                    <MenuItem value="OR">OR</MenuItem>
                                </Select>
                            </FormControl>
                            <TextField type="search" variant="outlined" label="Query 2"  value={booleanQuery2} onChange={(event) => setBooleanQuery2(event.target.value)} style={{ flex: 1 }}/>
                        </Stack>
                    </Grid>

                    <Grid item xs={12} style={{ marginTop: "1%" }}>
                        <Typography variant="p" className='advanced-search-title'>PROXIMITY SEARCH</Typography>
                        
                        <Stack spacing={2} direction="row" style={{ marginTop: "1.5%" }}>
                            <TextField type="search" variant="outlined" label="Term 1"  value={proximityTerm1} onChange={(event) => setProximityTerm1(event.target.value)} style={{ flex: 1 }}/>
                            <TextField type="search" variant="outlined" label="Term 2" value={proximityTerm2} onChange={(event) => setProximityTerm2(event.target.value)} style={{ flex: 1 }}/>
                            <TextField type="search" variant="outlined" label="Distance" value={proximityDistance} onChange={(event) => setProximityDistance(event.target.value)} style={{ flex: 1 }}/>
                        </Stack>
                    </Grid>

                    <Grid item xs={12} style={{ marginTop: "3%" }}>
                        <Stack spacing={0.5} direction="row" style={{ justifyContent: "center", alignItems: "center", cursor: "pointer" }} onClick={handleFiltersToggle}>
                            <Typography variant="p" className='advanced-search-title'>APPLY FILTERS</Typography>
                            { openFilters ? <ExpandLess/> : <ExpandMore/> }
                        </Stack>
                    </Grid>

                    <Grid item xs={12} style={{ marginTop: "1%" }}>
                        <Collapse in={openFilters}>
                            <BasicFilters checked={checked} dateRange={dateRange} setChecked={setChecked} setDateRange={setDateRange}/>
                            <Divider style={{ marginTop: "-12px"}}/>
                        </Collapse>
                    </Grid>


                    <Grid item xs={12} style={{ display: "flex", justifyContent: "center", flexDirection: "row", marginTop: "1%" }}>
                        <Button variant='contained' className='button-deco' type='submit' endIcon={<Search/>}>SEARCH</Button>
                    </Grid>
                    
                </Grid>
            </form>
        </div>
    )
}

export default AdvancedSearch;