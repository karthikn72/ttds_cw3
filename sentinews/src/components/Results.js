import React, { useEffect, useRef, useState } from 'react';
import { Grid, Modal, Box, useMediaQuery, useTheme, IconButton, Typography } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './Config/FirebaseConfig';
import { Close } from '@mui/icons-material';
import { HashLoader } from 'react-spinners';
import { modalStyle } from './Helper';
import { toast } from 'react-toastify';
import validator from 'validator';
import axios from 'axios';
import queryString from 'query-string';
import FilterPane from './Filters/FilterPane';
import ResultsPane from './ResultsPane';

function Results() {

    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation(); 

    const queryEndpoint = "/search"; 
    const prevSearch = useRef(location.search);
    const parameters = queryString.parse(window.location.search);
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    const [authState, setAuthState] = useState(false);
    const [resultsFound, setResultsFound] = useState(false);
    const [retrievalError, setRetrievalError] = useState("");
    const [openMobileFilters, setOpenMobileFilters] = useState(false);

    const [narrowFilters, setNarrowFilters] = useState(false);
    const [displayArticles, setDisplayArticles] = useState(false);
    const [showResultsPage, setShowResultsPage] = useState(false);

    const [query, setQuery] = useState("");
    const [sortBy, setSortBy] = useState("");
    const [queryType, setQueryType] = useState("");

    const [results, setResults] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [resultsCount, setResultsCount] = useState(0);
    const [responseTime, setResponseTime] = useState(0);

    const [sentimentsAvailable, setSentimentsAvailable] = useState(["Positive", "Neutral", "Negative"]);
    const [authorsAvailable, setAuthorsAvailable] = useState([]);
    const [categoriesAvailable, setCategoriesAvailable] = useState([]);
    const [publicationsAvailable, setPublicationsAvailable] = useState([]);

    const [dateRangeApplied, setDateRangeApplied] = useState([]);
    const [sentimentsApplied, setSentimentsApplied] = useState([]);
    const [authorsApplied, setAuthorsApplied] = useState([]);
    const [categoriesApplied, setCategoriesApplied] = useState([]);
    const [publicationsApplied, setPublicationsApplied] = useState([]);

    const handleMobileFilters = () => setOpenMobileFilters(open => !open);

    function sanitiseFilters(item) {
        const sanitisedFilter = item !== undefined && item !== null ? item.split(',') : [];
        return sanitisedFilter;
    }

    function filterUnusedItems(availableElements, appliedElements) {
        const unusedItems = availableElements.filter(element => 
            !appliedElements.map(item => item.toLowerCase()).includes(element.toLowerCase()));
        
        return unusedItems; 
    }

    const updateResults = (newPage) => {
        setDisplayArticles(false);
        const searchURL = `${process.env.REACT_APP_SENTINEWS_API_SERVER_URL}${queryEndpoint}${location.search}&page=${newPage}&request=articles`;

        axios.get(searchURL).then(response => {
            setResults(response.data.results);
            setTimeout(() => { setDisplayArticles(true); }, 1000);
        }).catch(error => { 
            if (error.response === undefined) {
                toast.error("Our API server is not accepting requests at the moment. Please try again later!", { toastId: 'server-error-1' });
            } else {
                const errorCode = error.response.status;

                if (errorCode === 404) {
                    toast.error("Unable to update results. Please try again later!", { toastId: 'update-results-error' }); 
                } else {
                    toast.error(`"We're experiencing an issue with our server at the moment. Please try again later! Error Code: ${errorCode}`, { toastId: 'server-error-2' }); 
                }
            }
            return navigate("/"); 
        });
    }

    const updateSort = (value) => {
        let filtersString = `q=${query}&type=${queryType}`

        filtersString += sentimentsApplied.length > 0 ? `&sentiment=${sentimentsApplied}` : '';
        filtersString += authorsApplied.length > 0 ? `&author=${authorsApplied}` : '';
        filtersString += categoriesApplied.length > 0 ? `&category=${categoriesApplied}` : '';
        filtersString += publicationsApplied.length > 0 ? `&publication=${publicationsApplied}` : '';
        filtersString += dateRangeApplied.length > 0 ? `&from=${dateRangeApplied[0]}&to=${dateRangeApplied[1]}` : '';

        filtersString += `&sortBy=${value}`;
        return navigate(`${queryEndpoint}?${filtersString}`);
    }

    const updatePage = (updateType, data) => {

        let filtersString = `q=${query}&type=${queryType}`;
        const [quantity, source, value] = data;
        const paramKeys = { sentiment: sentimentsApplied, author: authorsApplied, category: categoriesApplied, publication: publicationsApplied};

        const otherAppliedFilters = Object.entries(paramKeys).filter(([key, arr]) => key !== source && arr.length > 0).flatMap(([key, arr]) => `${key}=${arr}`).join("&");

        if (updateType === "remove") {
            if (quantity === "single") {
                if (value !== "date") {
                    const updatedFilter = paramKeys[source].filter(item => item !== value);
                    filtersString += updatedFilter.length > 0 ? `&${source}=${updatedFilter}` : '';
                    filtersString += dateRangeApplied.length > 0 ? `&from=${dateRangeApplied[0]}&to=${dateRangeApplied[1]}` : '';
                }
                filtersString += otherAppliedFilters.length > 0 ? `&${otherAppliedFilters}` : '';
            }
        } else {
            filtersString += source === "date" ? `&from=${value[0]}&to=${value[1]}` : `&${source}=${[...paramKeys[source], value]}`;
            filtersString += dateRangeApplied.length > 0 ? `&from=${dateRangeApplied[0]}&to=${dateRangeApplied[1]}` : '';
            filtersString += otherAppliedFilters.length > 0 ? `&${otherAppliedFilters}` : '';

        } 
        return navigate(`${queryEndpoint}?${filtersString}`);
    }

    useEffect(() => {
        if (location.search !== prevSearch.current) {
            window.location.reload();
            prevSearch.current = location.search;
        }

    }, [location.search]);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => { setAuthState(!!user); });
        return () => unsubscribe();
    }, []);

    useEffect(() => {
        const checkQuery = () => {
            //Define valid arguments
            const validSentiments = ["positive", "negative", "neutral"];
            const validSorts = ["relevance", "ascendingdate", "descendingdate"];
            const validQueryTypes = ["phrase", "boolean", "proximity", "freeform", "publication"];

            const singleParams = ["q", "type", "from", "to", "sortBy"];
            const duplicateOptionalParams = ["sentiment", "author", "publication", "category"];

            const validParams = [...singleParams, ...duplicateOptionalParams];

            //Checks for valid search term in query request
            if (!parameters.q) {
                toast.error("Please provide a search query to continue.", { toastId: 'empty-query' });
                return false;
            }

            //Checks for valid search type in query request
            if (!parameters.type) {
                toast.error("Please provide a search query type to continue.", { toastId: 'empty-query-type' });
                return false;
            }

            //Check for invalid parameters in query request
            for (const param in parameters) {
                if (!validParams.includes(param)) {
                    toast.error(`Invalid parameter "${param}" found in query. Please try again!`, { toastId: 'invalid-query' });
                    return false;
                }
            }

            //Check for duplicate filters in query request
            for (const param of singleParams) {
                if (parameters[param] && typeof parameters[param] !== 'string') {
                    toast.error(`Duplicate parameter "${param}" found in query. Please try again!`, { toastId: 'duplicate-single-optional-param' });
                    return false;
                }
            }

            for (const param of duplicateOptionalParams) {
                const value = sanitiseFilters(parameters[param]).map(str => str.toLowerCase());
                if (value && new Set(value).size < value.length) { 
                    toast.error(`Duplicate "${param}" filter found in query. Please try again!`, { toastId: 'duplicate-optional-param' });
                    return false;
                }
            }

            //Check for valid sentiments in query request
            const sentimentValues = sanitiseFilters(parameters.sentiment).map(str => str.toLowerCase());
            
            for (const item of sentimentValues) { 
                if (!validSentiments.includes(item)) {
                    toast.error(`Invalid sentiment "${item}" found in query. Please try again!`, { toastId: 'invalid-sentiment' });
                    return false; 
                }    
            }

            //Check for valid date range in query request
            const missingFrom = parameters.from === undefined && parameters.to !== undefined;
            const missingTo = parameters.to === undefined && parameters.from !== undefined;
            
            if (missingFrom || missingTo)  {
                toast.error(`Please provide a valid date range to continue.`, { toastId: 'invalid-date-range' });
                return false; 
            }

            if (parameters.from !== undefined && !validator.isDate(parameters.from)) {
                toast.error(`Invalid date found in "from" parameter. Please try again!`, { toastId: 'invalid-from-date' });
                return false;
            }

            if (parameters.to !== undefined && !validator.isDate(parameters.to)) {
                toast.error(`Invalid date found in "to" parameter. Please try again!`, { toastId: 'invalid-to-date' });
                return false;
            }

            //Check for valid sort selection in query request
            if (parameters.sortBy !== undefined && !validSorts.includes(parameters.sortBy.toLowerCase())) {
                toast.error(`Invalid sort-by type "${parameters.sortBy}" found in query. Please try again!`, { toastId: 'invalid-sort' });
                return false;
            }

            //Check for valid querty types in query request
            if (!validQueryTypes.includes(parameters.type.toLowerCase())) {
                toast.error(`Invalid search type "${parameters.type}" found in query. Please try again!`, { toastId: 'invalid-query-type' });
                return false;
            }

            return true;
        }

        const validQuery = checkQuery();
 
        if (validQuery) {
            setQuery(parameters.q);
            setQueryType(parameters.type);
            setSortBy(parameters.type.toLowerCase() === "publication" ? (parameters.sortBy || "descendingdate") : (parameters.sortBy || "relevance"));

            const dateRange = [parameters.from, parameters.to].filter(param => param !== undefined);            
            const sentiments = sanitiseFilters(parameters.sentiment);
            const authors = sanitiseFilters(parameters.author);
            const categories = sanitiseFilters(parameters.category);
            const publications = sanitiseFilters(parameters.publication);

            setDateRangeApplied(dateRange);
            setSentimentsApplied(sentiments);
            setAuthorsApplied(authors);
            setCategoriesApplied(categories);
            setPublicationsApplied(publications);

            const searchURL = `${process.env.REACT_APP_SENTINEWS_API_SERVER_URL}${queryEndpoint}${location.search}&page=0&request=meta`;

            axios.get(searchURL).then(result => {
                console.log(result);
                const filterOptions = result.data.filter_options;

                const results = result.data.results;
                setResultsFound(true);
                
                if (results === undefined) {
                    setNarrowFilters(true);
                } else {
                    setResults(results);
                    setResultsCount(result.data.total_results);
                    setResponseTime(result.data.retrieval_time);
    
                    setSentimentsAvailable(filterUnusedItems(sentimentsAvailable, sentiments));
                    setAuthorsAvailable(filterUnusedItems(filterOptions.authors, authors));
                    setCategoriesAvailable(filterUnusedItems(filterOptions.sections, categories));
                    setPublicationsAvailable(filterUnusedItems(filterOptions.publications, publications));
    
                    setDisplayArticles(true);
                }

                setTimeout(() => { setShowResultsPage(true); }, 700);
            }).catch(error => { 
                console.log(error);
                if (error.response === undefined) {
                    toast.error("Our API server is not accepting requests at the moment. Please try again later!", { toastId: 'server-error-1' });
                    return navigate("/"); 
                } else {
                    const errorCode = error.response.status;

                    if (errorCode === 404) {
                        setResultsFound(false);
                        setRetrievalError(error.response.data.message);
                        setTimeout(() => { setShowResultsPage(true); }, 700);
                    } else if (errorCode === 400) {
                        toast.error("Your search query is incorrectly formatted. Please try again!", { toastId: 'bad-query' });
                        return navigate("/"); 
                    } else {
                        toast.error(`We're experiencing an issue with our server at the moment. Please try again later! Error Code: ${errorCode}`, { toastId: 'server-error-2' });
                        return navigate("/"); 
                    } 
                }
            });

        } else {
            return navigate("/");
        }
    // eslint-disable-next-line
    }, []);

    if (!showResultsPage) {
        return (
            <div className='wrapper'>
                <div className='cover'>
                    <HashLoader/>
                </div>
            </div>
        );
    }

    return(
        <div>
            <Grid container spacing={0} style={{ minHeight: "100vh", height: "auto",  overflowY: "auto" }}>        

                { resultsFound && !isMobile ?
                    <Grid item xs={5} style={{ maxWidth: "285px" }}> 
                        <FilterPane updatePage={updatePage} dateRangeApplied={dateRangeApplied} sentimentsApplied={sentimentsApplied} sentimentsAvailable={sentimentsAvailable} authorsApplied={authorsApplied} authorsAvailable={authorsAvailable} categoriesApplied={categoriesApplied} categoriesAvailable={categoriesAvailable} publicationsApplied={publicationsApplied} publicationsAvailable={publicationsAvailable} queryType={queryType}/>
                    </Grid> 
                : null }

                <Grid item xs={"auto"} style={{ flex: 1 }}>
                    <ResultsPane updateResults={updateResults} updatePage={updatePage} isMobile={isMobile} handleMobileFilters={handleMobileFilters} resultsFound={resultsFound} updateSort={updateSort} query={query} setQuery={setQuery} sortBy={sortBy} results={results} resultsCount={resultsCount} responseTime={responseTime} currentPage={currentPage} setCurrentPage={setCurrentPage} displayArticles={displayArticles} narrowFilters={narrowFilters} retrievalError={retrievalError} queryType={queryType} authState={authState}/> 
                </Grid>

            </Grid>

            { isMobile ? 
                <div>
                    <Modal open={openMobileFilters} onClose={handleMobileFilters}>
                        <Box sx={modalStyle} style={{ width: "80%", height: "80%", overflowY: "scroll" }}>
                            <Box sx={{ m: 0.25 }}/>
                            <Typography variant="h6" align="center">FILTER SEARCH RESULTS</Typography>
                            <IconButton style= {{ position: "absolute", top: "0", right: "0", margin: "10px"}} onClick={handleMobileFilters}>
                                <Close/>
                            </IconButton>
                            <div style={{ marginTop: "20px" }}>
                                <FilterPane updatePage={updatePage} dateRangeApplied={dateRangeApplied} sentimentsApplied={sentimentsApplied} sentimentsAvailable={sentimentsAvailable} authorsApplied={authorsApplied} authorsAvailable={authorsAvailable} categoriesApplied={categoriesApplied} categoriesAvailable={categoriesAvailable} publicationsApplied={publicationsApplied} publicationsAvailable={publicationsAvailable} queryType={queryType}/>
                            </div>
                        </Box>
                    </Modal>
                </div> 
            : null }
        </div>
    )
}

export default Results;