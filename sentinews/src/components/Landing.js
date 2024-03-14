import React, { useState } from 'react';
import fullLogo from '../images/logo.png';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { getQueryType, modalStyle } from './Helper';
import { Button, Stack, Box, Modal } from '@mui/material';
import { Search, ContentPasteSearch } from '@mui/icons-material';

import SearchBar from './Search/SearchBar';
import SearchBarFilters from './Search/SearchBarFilters';
import AdvancedSearch from './Search/AdvancedSearch';
import TrendingNews from './TrendingNews';

function Landing() {
    const navigate = useNavigate();
    const [query, setQuery] = useState("");

    const [openFilters, setOpenFilters] = useState(false);
    const [openAdvanced, setOpenAdvanced] = useState(false);

    const handleFiltersToggle = () => setOpenFilters(state => !state);
    const handleAdvancedToggle = () => setOpenAdvanced(state => !state);

    const submitQuery = (e) => {
        e.preventDefault();

        const sanitisedQuery = query.trim();

        if (sanitisedQuery.length < 1) {
            return toast.error("Please provide a search query to continue.", { toastId: 'empty-query' });
        } else {
            const queryType = getQueryType(sanitisedQuery);
            setQuery(sanitisedQuery);
            toast.dismiss();
            return navigate(`/search?q=${query}&type=${queryType}`);
        }
    }

    return(
        <div className='wrapper'>
            <div className='cover'>
                <img src={fullLogo} width="80%" height="auto" alt="Sentinews Logo" style={{ maxWidth: "400px", marginBottom: "15px" }}/>
                <h4 style={{ fontWeight: "bold", fontSize: "17px", marginBottom: "20px" }}>The Sentiment-Based News Search Engine</h4>
                
                <div style={{width: "90%", maxWidth: "900px" }}>
                    <SearchBar query={query} setQuery={setQuery} submitQuery={submitQuery} viewFilters={handleFiltersToggle}/>
                </div>

                <Stack style={{ marginTop: "24px" }} direction="row" spacing={2}>
                    <Button variant='contained' className='button-deco' onClick={submitQuery} endIcon={<Search/>}>SEARCH</Button>
                    <Button variant='contained' className='button-deco' onClick={handleAdvancedToggle} endIcon={<ContentPasteSearch/>}>ADVANCED OPTIONS</Button>
                </Stack>
                <TrendingNews/>
            </div>

            <div>
                <Modal open={openFilters} onClose={handleFiltersToggle}>
                    <Box sx={modalStyle} style={{ width: "90%", maxWidth: 750, height: "68%", maxHeight: 640 }}>
                        <SearchBarFilters handleClose={handleFiltersToggle} query={query} setQuery={setQuery}/>
                    </Box>
                </Modal>
            </div>
            
            <div>
                <Modal open={openAdvanced} onClose={handleAdvancedToggle}>
                    <Box sx={modalStyle} style={{ width: "80%", maxWidth: 600, height: "90%", maxHeight: 620 }}>
                        <AdvancedSearch handleClose={handleAdvancedToggle}/>
                    </Box>
                </Modal>
            </div>
        </div>
    )
}

export default Landing;