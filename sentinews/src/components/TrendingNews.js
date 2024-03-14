import React, { Fragment, useEffect, useState } from 'react';
import { Typography, Box, Stack } from '@mui/material';
import { toast } from 'react-toastify';
import axios from 'axios';
function TrendingNews() {

    const [trendingArticles, setTrendingArticles] = useState([]);
    const [displayTrending, setDisplayTrending] = useState(false);

    useEffect(() => {
        const retrieveTrending = async () => {
            const queryURL = `${process.env.REACT_APP_SENTINEWS_API_SERVER_URL}/get_live?type=trending`;

            axios.get(queryURL).then(result => {
                const results = result.data.trending;
                setTrendingArticles(results);
                setDisplayTrending(true);
            }).catch(error => { 
                if (error.response !== undefined) {
                    const errorCode = error.response.status;

                    if (errorCode === 404) {
                        toast.error("Unable to load the trending articles. Please try again later!", { toastId: 'trending-error' }); 
                    } else {
                        toast.error(`"We're experiencing an issue with our server at the moment. Please try again later! Error Code: ${errorCode}`, { toastId: 'server-error-2' }); 
                    }
                }
            });
        } 
        
        retrieveTrending();
    // eslint-disable-next-line
    }, []);

    return(
        <div>
            {displayTrending ? <Fragment>
                <div style={{ height: "230px", marginTop: "20px" }}>

                    <Typography variant="subtitle2" className='trending-text'>TRENDING NEWS</Typography>
                    <Stack spacing={1} direction="column" style={{ width: "390px", marginTop: "10px" }}>
                        { trendingArticles.map((article, index) => {
                            return (
                                <Box key={index} sx={{ padding: "5px", width: "390px", cursor: "pointer", '&:hover': { textDecoration: 'underline' }}} onClick={() => window.open(article.url, '_blank')}>
                                    <Typography variant="subtitle2" style={{ fontSize: "15px", fontWeight: "bold", textAlign: "center" }}>{article.title.length > 45 ? article.title.substring(0,44) + "..." : article.title}</Typography>  
                                </Box>
                            )
                        })}
                    </Stack>

                </div>
            </Fragment> : <Box style={{ height: "230px", marginTop: "20px" }}/> }
        </div>
    )
}

export default TrendingNews;