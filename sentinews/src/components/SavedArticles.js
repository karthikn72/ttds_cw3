import React, { useEffect, useState, useRef, Fragment } from 'react';
import { Grid, Box, Pagination, Stack, Typography, useTheme, useMediaQuery } from '@mui/material';
import emptyArticles from '../images/empty-articles-saved.svg';
import { onAuthStateChanged } from 'firebase/auth';
import { paginate, readStorage } from './Helper';
import { useNavigate } from 'react-router-dom';
import { auth } from './Config/FirebaseConfig';
import { HashLoader } from 'react-spinners';
import { toast } from 'react-toastify';
import axios from 'axios';
import ArticleBox from './ArticleBox/ArticleBox';

function SavedArticles() {

    const theme = useTheme();
    const navigate = useNavigate();
    const scrollRef = useRef(null);
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    const [showPage, setShowPage] = useState(false);
    const [authState, setAuthState] = useState(false);
    const [savedArticlesExist, setSavedArticlesExist] = useState(false);

    const [currentPage, setCurrentPage] = useState(1);
    const [paginatedList, setPaginatedList] = useState([]);
    const [currentArticles, setCurrentArticles] = useState([]);

    const handlePageChange = (_, newPage) => {
        if (currentPage !== newPage) {
            setCurrentArticles(paginatedList[newPage - 1]);
            setCurrentPage(newPage);
            scrollRef.current.scrollIntoView({ behavior: 'smooth'});
        }
    }

    useEffect(() => {

        const retrieveSaved = async (savedArticles) => {
            const queryURL = `${process.env.REACT_APP_SENTINEWS_API_SERVER_URL}/get_saved_articles?article_ids=${savedArticles}`;

            axios.get(queryURL).then(result => {
                const results = result.data.saved_articles;
                const paginatedResults = paginate(results, process.env.REACT_APP_ARTICLES_PER_PAGE);
                setPaginatedList(paginatedResults);
                setCurrentArticles(paginatedResults[currentPage - 1]);
                setAuthState(auth.currentUser !== null);
                setTimeout(() => { setShowPage(true); }, 2000);
            }).catch(error => { 
                if (error.response === undefined) {
                    toast.error("Our API server is not accepting requests at the moment. Please try again later!", { toastId: 'server-error-1' });
                } else {
                    const errorCode = error.response.status;

                    if (errorCode === 404) {
                        toast.error("Unable to find your saved articles. Please try again later!", { toastId: 'saved-articles-error' }); 
                    } else {
                        toast.error(`"We're experiencing an issue with our server at the moment. Please try again later! Error Code: ${errorCode}`, { toastId: 'server-error-2' }); 
                    }
                }
                return navigate("/");  
            });
        } 

        const unsubscribe = onAuthStateChanged(auth, (user) => {
            const userState = !!user;

            readStorage(userState).then((savedArticles) => {
                const articlesExist = savedArticles.length > 0;
                setSavedArticlesExist(articlesExist);
                if (articlesExist) {
                    retrieveSaved(savedArticles);
                } else {
                    setTimeout(() => { setShowPage(true); }, 2000);
                }
            })
        });

        return () => unsubscribe();
    // eslint-disable-next-line 
    }, []);

    if (!showPage) {
        return (
            <div className='wrapper'>
                <div className='cover'>
                    <HashLoader/>
                </div>
            </div>
        );
    }

    return(
        <Grid container direction="column" spacing={0} style={{ height: "100%", width: "100%" }}>
            { savedArticlesExist ? <Fragment> 
                <Grid ref={scrollRef} item style={{ height: "auto", width: "100%"}}>
                    <Box className='center-page' style={{ margin: "25px auto" }}>
                        <Typography variant="h5">SAVED ARTICLES</Typography>
                    </Box>
                </Grid>

                <Grid item style={{ height: "auto", width: "100%"}}>
                    <Box className='center-page' style={{ margin: "auto" }}>
                        <Stack spacing={2.5} direction="column" style={{ width: "100%" }}>
                            { currentArticles.map((article, index) => {
                                return (
                                    <ArticleBox key={index} authState={authState} updatePage={undefined} article={article} page={"saved"}/>
                                ) 
                            })}
                        </Stack> 
                    </Box>
                </Grid>
                
                <Grid item style={{ height: "auto", width: "100%"}}>
                    <Box className='center-page' style={{ margin: "30px auto" }}>
                        <Pagination size={ isMobile ? "small" : "large"} count={paginatedList.length} page={currentPage} onChange={handlePageChange} color='primary' boundaryCount={ isMobile ? 2 : 3 } showFirstButton showLastButton/>
                    </Box>
                </Grid> 
            </Fragment> : 
            <div className='wrapper'>
                <div className='cover'>
                    <img src={emptyArticles} width="25%" height="100%" style={{ padding: "5px", maxWidth: "180px", minHeight: "180px" }} alt="Empty Articles Logo"/>
                    <div className='error-text'>
                        <p>You haven't saved any articles to read later</p>
                    </div>
                </div>
            </div> }
        </Grid>
    )
}

export default SavedArticles;