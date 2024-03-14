import React, { Fragment, useEffect, useState, useRef } from 'react';
import { Grid, Stack, Modal, Box, Divider, Button, Typography, FormControl, InputLabel, Select, MenuItem, Pagination } from '@mui/material';
import { ContentPasteSearch, FilterAlt } from '@mui/icons-material';
import narrowResults from '../images/narrow-filters.svg';
import noResults from '../images/no-results.svg';
import { getQueryType, modalStyle } from './Helper';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import SearchBar from './Search/SearchBar';
import SearchBarFilters from './Search/SearchBarFilters';
import AdvancedSearch from './Search/AdvancedSearch';
import ArticleBoxSkeleton from './ArticleBox/ArticleBoxSkeleton';
import ArticleBox from './ArticleBox/ArticleBox';

function ResultsPane({ updateResults, updatePage, isMobile, handleMobileFilters, resultsFound, updateSort, query, setQuery, sortBy, results, resultsCount, responseTime, currentPage, setCurrentPage, displayArticles, narrowFilters, retrievalError, queryType, authState }) {
                                                                                                                                                                                                                                               
    const scrollRef = useRef(null);
    const navigate = useNavigate();

    const [openFilters, setOpenFilters] = useState(false);
    const [openAdvanced, setOpenAdvanced] = useState(false);

    const [paginatedList, setPaginatedList] = useState([]);
    const [currentArticles, setCurrentArticles] = useState([]);

    const [currentRequestPage, setCurrentRequestPage] = useState(0);

    const handleFiltersToggle = () => setOpenFilters(state => !state);
    const handleAdvancedToggle = () => setOpenAdvanced(state => !state);

    const articlesPerPage = process.env.REACT_APP_ARTICLES_PER_PAGE;
    const totalPageCount = Math.ceil(resultsCount / articlesPerPage);

    const parsedRetrievalTime = parseFloat(responseTime).toFixed(6);
    const parsedResultsCount = parseFloat(resultsCount).toLocaleString('en-US', {minimumFractionDigits: 0});

    const convertPageToIndex = (pageNumber) => { return (pageNumber % 10 || 10) - 1; };

    const handlePageChange = (_, newPage) => {

        if (currentPage !== newPage) {
            const newRequestPage = Math.ceil(newPage/articlesPerPage) - 1;

            const notDirectSwitch = (newPage !== currentPage + 1) && (newPage !== currentPage - 1);
            const switchingTenRight = currentPage % 10 === 0 && newPage === currentPage + 1;
            const switchingTenLeft = newPage % 10 === 0 && newPage === currentPage - 1;
            const switchingMultipleSections = currentRequestPage !== newRequestPage && notDirectSwitch;

            if (switchingTenRight || switchingTenLeft || switchingMultipleSections) {
                setCurrentRequestPage(newRequestPage);
                updateResults(newRequestPage);
            } else {
                const newArticles = paginatedList[convertPageToIndex(newPage)];
                setCurrentArticles(newArticles);
            }
            setCurrentPage(newPage);
            scrollRef.current.scrollIntoView({ behavior: 'smooth'});
        }
    }

    useEffect(() => {
        const paginatedArticles = Array.from( {length: totalPageCount}, (_, index) =>  results.slice(index * articlesPerPage, (index + 1) * articlesPerPage)); 
        const firstPageArticles = paginatedArticles[convertPageToIndex(currentPage)];

        setPaginatedList(paginatedArticles);
        setCurrentArticles(firstPageArticles); 
    // eslint-disable-next-line
    }, [results]);

    const submitQuery = (e) => { 
        e.preventDefault();

        const sanitisedQuery = query.trim();

        if (sanitisedQuery.length < 1) {
            return toast.error("Please provide a search query to continue.", { toastId: 'empty-query' });
        } else {
            setQuery(sanitisedQuery);
            toast.dismiss();
            return navigate(`/search?q=${query}&type=${getQueryType(sanitisedQuery)}`);
        }
    }

    return(
        <div>
            <Grid container direction="column" spacing={0} style={{ height: "100%", width: "100%" }}>
                
                <Grid ref={scrollRef} item style={{ height: "auto", width: "100%"}}>
                    <div className='center-page' style={{ margin: "10px auto" }}>
                        <SearchBar query={query} setQuery={setQuery} submitQuery={submitQuery} viewFilters={handleFiltersToggle} />
                    </div>
                    <Divider style={{ backgroundColor: "#242526" }}/>
                </Grid>

                { resultsFound ? <Fragment>

                    { !narrowFilters ? <Fragment> 
                        <Grid item style={{ height: "auto", width: "100%"}}>
                            { isMobile ? <Typography className='center-page' variant="subtitle2" style={{ fontSize: "14px", textAlign: "center", margin: "15px auto" }}>About {parsedResultsCount} results ({parsedRetrievalTime} seconds)</Typography> : null }

                            <Box className='center-page' style={{ margin: isMobile ? "20px auto" : "5px auto" }}>
                                <Stack direction="row" spacing={isMobile ? 5 : 0 } alignItems="center" justifyContent={ isMobile ? "center" : "space-between"} style={{ width: "100%", margin: isMobile ? "0px" : "10px" }}>
                                    { isMobile ?      
                                        <Button variant='contained' className='button-deco' startIcon={<FilterAlt/>} onClick={handleMobileFilters}>FILTER RESULTS</Button>
                                        : <Typography variant="subtitle2" style={{ fontSize: "14px" }}>About {parsedResultsCount} results ({parsedRetrievalTime} seconds)</Typography> 
                                    }
                                    <FormControl size='small'>
                                        <InputLabel id="sort-by-select">Sort By</InputLabel>
                                        <Select labelId="sort-by-select" value={sortBy} label="Sort By" onChange={(event) => { updateSort(event.target.value); }}>
                                            { queryType.toLowerCase() !== "publication" ? <MenuItem value={"relevance"}>Relevance</MenuItem> : null }
                                            <MenuItem value={"descendingdate"}>Date (Newest)</MenuItem>
                                            <MenuItem value={"ascendingdate"}>Date (Oldest)</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Stack>
                            </Box>
                        </Grid>

                   
                        <Grid item style={{ height: "auto", width: "100%"}}>
                            <Box className='center-page' style={{ margin: "5px auto" }}>
                                <Stack spacing={2.5} direction="column" style={{ width: "100%" }}>
                                    {displayArticles ? 
                                        currentArticles.map((article, index) => {
                                            return (
                                                <ArticleBox key={index} authState={authState} updatePage={updatePage} article={article} page={"results"}/>
                                            )
                                        }) 
                                    : Array.from({ length: currentPage === paginatedList.length ? resultsCount % articlesPerPage : articlesPerPage }).map((_, index) => {
                                        return (
                                            <ArticleBoxSkeleton key={index}/>
                                        )
                                    })}
                                </Stack> 
                            </Box>
                        </Grid> 

                        <Grid item style={{ height: "auto", width: "100%"}}>
                            <Box className='center-page' style={{ margin: "20px auto" }}>
                                <Pagination size={ isMobile ? "small" : "large"} count={paginatedList.length} page={currentPage} onChange={handlePageChange} color='primary' showFirstButton showLastButton/>
                            </Box>
                        </Grid>  
                    </Fragment>: <Grid item style={{ height: "auto", width: "100%"}}>
                         <div className='cover' style={{ marginTop: "180px" }}>
                            <img src={narrowResults} width="25%" height="100%" style={{ padding: "5px", marginBottom: "10px", maxWidth: "180px", minHeight: "180px" }} alt="Narrow Filters Logo"/>
                            <div className='error-text'>
                                <h6 style={{ marginBottom: "15px", fontWeight: "bold" }}>About {parsedResultsCount} results found ({parsedRetrievalTime} seconds)</h6>
                                <p style={{ fontSize: "15px", lineHeight: "1.75" }}>We couldn't find any search results with your current filters. <br/> Please try removing some filters or broadening your search terms.</p>
                            </div>
                            { isMobile ? <Stack direction="row" alignItems="center" justifyContent={"center"} style={{ width: "100%", margin: "10px" }}>
                                <Button variant='contained' className='button-deco' startIcon={<FilterAlt/>} onClick={handleMobileFilters}>FILTER RESULTS</Button>
                            </Stack> : null }
                        </div>
                    </Grid> }

                </Fragment> : <Grid item style={{ height: "100%", width: "100%" }}>
                    <div className='cover' style={{ marginTop: "180px" }}>
                        <img src={noResults} width="25%" height="100%" style={{ padding: "5px", marginBottom: "10px", maxWidth: "180px", minHeight: "180px" }} alt="Empty Articles Logo"/>
                        <div className='error-text'>
                            <h4 style={{ marginBottom: "15px" }}>Well, this is awkward.</h4>
                            <p style={{ fontSize: "15px", lineHeight: "1.75" }}>{ retrievalError.length === 0 ? "We couldn't find any results for your search query." : retrievalError }<br/>Please try rephrasing your query, or explore our advanced search options below.</p>
                        </div>
                        <Button style={{ marginTop: "6px" }} variant='contained' className='button-deco' onClick={handleAdvancedToggle} endIcon={<ContentPasteSearch/>}>ADVANCED OPTIONS</Button>
                    </div>
                </Grid> }
            </Grid>
                
            <div>
                <Modal open={openFilters} onClose={handleFiltersToggle}>
                    <Box sx={modalStyle} style={{ width: "90%", maxWidth: 750, height: "68%", maxHeight: 640 }}>
                        <SearchBarFilters handleClose={handleFiltersToggle} query={query} setQuery={setQuery}/>
                    </Box>
                </Modal>
            </div>

            <div>
                <Modal open={openAdvanced} onClose={handleAdvancedToggle}>
                    <Box sx={modalStyle} style={{ width: "90%", maxWidth: 600, height: "90%", maxHeight: 620 }}>
                        <AdvancedSearch handleClose={handleAdvancedToggle}/>
                    </Box>
                </Modal>
            </div>
        </div>
    )
}


export default ResultsPane;