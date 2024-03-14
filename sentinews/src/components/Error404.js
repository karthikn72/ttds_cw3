import React from 'react';
import errorLogo from '../images/404.svg';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import HomeSharpIcon from '@mui/icons-material/HomeSharp';

function Error404() {
    const navigate = useNavigate();

    function navigateHome() { return navigate("/"); }

    return(
        <div className='wrapper'>
            <div className='cover'>
                <img src={errorLogo} width="100%" height="auto" style={{ maxWidth: "240px", marginBottom: "17.5px" }} alt="404 Logo"/>
                <div className='error-text'>
                    <p>Uh-oh! The page you're looking for seems to have wandered off.<br/>
                    Feel free to head back to our homepage and keep exploring with<br/> Sentinews, your global source for news!</p>
                </div>
                
                <Button variant='contained' className='button-deco' startIcon={<HomeSharpIcon/>} onClick={navigateHome}>BACK TO HOME</Button>
            </div>
        </div>
    )
}

export default Error404;