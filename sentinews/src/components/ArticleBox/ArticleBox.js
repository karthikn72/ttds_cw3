import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardActions, Typography, Chip, Stack, Button, Box, IconButton, Tooltip } from '@mui/material';
import { doc, updateDoc, arrayUnion, arrayRemove, getDoc, setDoc } from 'firebase/firestore';
import { Share, BookmarkBorder, BookmarkRemove } from '@mui/icons-material';
import { auth, db } from '../Config/FirebaseConfig';
import { RWebShare } from 'react-web-share';
import { format } from 'date-fns';
import queryString from 'query-string';
import { readStorage } from '../Helper';

function ArticleBox({authState, updatePage, article, page}) {

    let iconClass = "";
    const parameters = queryString.parse(window.location.search);
    const savedArticlesKey = process.env.REACT_APP_SAVED_ARTICLES_KEY;
    const [articleSaved, setArticleSaved] = useState();
    const [displayButtons, setDisplayButtons] = useState(false);

    const parseDate = (dateString) => { return format(new Date(dateString), 'dd MMM yyyy HH:mm'); }

    const parseAuthor = (author) => {
        const authorString = author.length > 1 ? "MULTIPLE AUTHORS" : author.join("");
        return authorString === "" ? "BY UNKNOWN" : `BY ${authorString}`;
    }

    const parseSnippet = (snippet) => {
        return snippet.length > 0 ? snippet : "No text available for this article."
    }

    const snippet =  parseSnippet(article.article);
    const unique_id = article.article_id;
    const author = parseAuthor(article.author_names);
    const publisher = article.publication_name;
    const category = article.section_name;
    const title = article.title;
    const publish_date = parseDate(article.upload_date);
    const url = article.url;
    const sentiment = article.sentiment;

    switch (sentiment) {
        case "Positive": 
            iconClass = "green"; 
            break;
        case "Neutral":
            iconClass = "orange";
            break;
        case "Negative":
            iconClass = "#dc0000";
            break;
        default:
            iconClass = "white";
            break;
    } 

    useEffect(() => {
        readStorage(authState).then((savedArticles) => {
            setArticleSaved(savedArticles.includes(unique_id));
            setDisplayButtons(true);
        }) 
    // eslint-disable-next-line
    }, [article]); 

    const handleCategory = (category, value) => {

        if (parameters[category] === undefined || !parameters[category].includes(value)) {
            updatePage("add", ["", category, value]); 
        }
    }

    const handleSaveToggle = async (id) => {
        let updatedArticles = [];
        const savedArticles = await readStorage(authState);

        if (authState) {
            const docRef = doc(db, savedArticlesKey, auth.currentUser.uid);

            if (articleSaved) {
                await updateDoc(docRef, { articles: arrayRemove(id) });
            } else {
                const docSnap = await getDoc(docRef);

                if (docSnap.exists()) {
                    await updateDoc(docRef, { articles: arrayUnion(id) });
                } else {
                    await setDoc(docRef, { articles: [id] });
                } 
            }
        } else {
            updatedArticles = articleSaved ? savedArticles.filter(item => item !== id) : [...savedArticles, id];
            localStorage.setItem(savedArticlesKey, JSON.stringify(updatedArticles));
        }
        setArticleSaved(!articleSaved);

        if (page === "saved") {
            window.location.reload();
        }
    }

    return(
        <Card sx={{ width: "100%", height: "100%" }}>
            <CardContent style={{ paddingBottom: "0px", width: "100%", height: "100%" }}>
                <Stack>
                    <Typography variant="subtitle2" className="article-publication">{publisher}</Typography>
                    <Typography variant="subtitle1" className="article-title">{title}</Typography>
                    <Stack direction="row" spacing={1}>
                        { sentiment !== "" ? <Chip className="article-chip" size="small" variant="outlined" label={sentiment} onClick={page === "results" ? () => handleCategory("sentiment", sentiment) : undefined } icon={<div className="sentiment-status" style={{ backgroundColor: iconClass}}/>} sx={{ '& .sentiment-status': {marginLeft: "10px", marginRight: "2px"} }}/> : null }
                        { category !== "" ? <Chip className="article-chip" size="small" variant="outlined" label={category} onClick={page === "results" ? () => handleCategory("category", category) : undefined }/> : null }
                    </Stack>
                    <Box style={{ width: "100%" }}>
                        <Typography variant="subtitle2" className="article-snippet">{snippet}</Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                        <Typography variant="subtitle2" className="article-footer">{publish_date}</Typography>
                        <Typography variant="subtitle2" className="article-footer">•</Typography>
                        <Typography variant="subtitle2" className="article-footer">{author}</Typography>
                    </Stack>
                </Stack>
            </CardContent>

            <CardActions style={{ justifyContent: "space-between", height: "64px" }}>
                <Button onClick={() => window.open(url, '_blank')}>View Article</Button>
                { displayButtons ? 
                <Stack direction="row" spacing={1.5}>
                    <RWebShare data={{ title: `SentiNews - Share Article`, url: url, text: "SentiNews - Share Article" }}>
                        <Tooltip title="Share Article">
                            <IconButton size="large" className="article-icon">
                                <Share/>
                            </IconButton>
                        </Tooltip>
                    </RWebShare> 


                    <Tooltip title={articleSaved ? "Remove from Saved Stories" : "Save for Later"}>
                        <IconButton size="large" className="article-icon" onClick={() => handleSaveToggle(unique_id)}>
                            { articleSaved ? <BookmarkRemove/> : <BookmarkBorder/> }
                        </IconButton>
                    </Tooltip> 
                </Stack> : null }          
            </CardActions>
        </Card>
    )
}

export default ArticleBox;