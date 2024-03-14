import React, { useState } from 'react';
import { Grid, Paper } from '@mui/material';
import Sentiment from './FilterCategories/Sentiment';
import CurrentFilters from './FilterCategories/CurrentFilters';
import DateRangeSelector from './FilterCategories/DateRangeSelector';
import QuerySpecificFilters from './FilterCategories/QuerySpecificFilters';

function FilterPane({updatePage, dateRangeApplied, sentimentsApplied, sentimentsAvailable, authorsApplied, authorsAvailable, categoriesApplied, categoriesAvailable, publicationsApplied, publicationsAvailable, queryType}) {

    const filtersSelected = (dateRangeApplied.length > 0 
        || sentimentsApplied.length > 0 || authorsApplied.length > 0 
        || categoriesApplied.length > 0 || publicationsApplied.length > 0
    );

    const [dateExpand, setDateExpand] = useState(true);
    const [sentimentExpand, setSentimentExpand] = useState(true);
    const [authorExpand, setAuthorExpand] = useState(true);
    const [categoryExpand, setCategoryExpand] = useState(true);
    const [publicationExpand, setPublicationExpand] = useState(true);

    const handleDateExpand = () => setDateExpand((expand) => !expand);
    const handleSentimentExpand = () => setSentimentExpand((expand) => !expand);
    const handleAuthorExpand = () => setAuthorExpand((expand) => !expand);
    const handleCategoryExpand = () => setCategoryExpand((expand) => !expand);
    const handlePublicationExpand  = () => setPublicationExpand((expand) => !expand);
    
    return(
        <Paper square style={{ height: "100%" }}>
            <Grid container direction="column" spacing={0} style={{ height: "100%", width: "100%" }}>
                <Grid item style={{ height: "auto", maxWidth: "100%"}}>
                    { filtersSelected ? <CurrentFilters updatePage={updatePage} dateRangeApplied={dateRangeApplied}  sentimentsApplied={sentimentsApplied} authorsApplied={authorsApplied} categoriesApplied={categoriesApplied} publicationsApplied={publicationsApplied}/>  : null }
                </Grid>

                <Grid item style={{ height: "auto", maxWidth: "100%" }}>
                    { dateRangeApplied.length === 0 ? <DateRangeSelector updatePage={updatePage} expand={dateExpand} handleExpand={handleDateExpand}/> : null }
                </Grid>

                <Grid item style={{ height: "auto", maxWidth: "100%" }}>
                    { authorsAvailable.length > 0 ? <QuerySpecificFilters updatePage={updatePage} name={"AUTHOR"} filterType={"author"} expand={authorExpand} handleExpand={handleAuthorExpand} optionsAvailable={authorsAvailable}/> : null }
                </Grid>

                <Grid item style={{ height: "auto", maxWidth: "100%" }}>
                    { categoriesAvailable.length > 0 ? <QuerySpecificFilters updatePage={updatePage} name={"CATEGORY"} filterType={"category"} expand={categoryExpand} handleExpand={handleCategoryExpand} optionsAvailable={categoriesAvailable}/> : null }
                </Grid>

                { queryType.toLowerCase() !== "publication" ? <Grid item style={{ height: "auto", maxWidth: "100%" }}>
                    { publicationsAvailable.length > 0 ? <QuerySpecificFilters updatePage={updatePage} name={"PUBLICATION"} filterType={"publication"} expand={publicationExpand} handleExpand={handlePublicationExpand} optionsAvailable={publicationsAvailable}/> : null }
                </Grid> : null }

                <Grid item style={{ height: "auto", maxWidth: "100%" }}>
                    { sentimentsAvailable.length > 0 ? <Sentiment updatePage={updatePage} expand={sentimentExpand} handleExpand={handleSentimentExpand} sentimentsAvailable={sentimentsAvailable}/> : null }
                </Grid>
            </Grid>
        </Paper>
    )
}

export default FilterPane;