import React from 'react';
import { Card, CardContent, Skeleton, CardActions, Typography, Avatar, Stack } from '@mui/material';

function ArticleBoxSkeleton() {
    
    return(
        <Card sx={{ width: "100%", height: "100%" }}>
            <CardContent style={{ width: "100%", height: "100%" }}>
                <Stack>
                    <Typography variant="subtitle2"><Skeleton animation="wave" style={{ width: "15%" }}/></Typography>
                    <Typography variant="subtitle1"><Skeleton animation="wave" style={{ width: "60%" }}/></Typography>
                    <Skeleton animation="wave" style={{ width: "25%" }}/>
                    <Skeleton animation="wave" variant="rounded" style={{ width: "100%", height: "70px" }} />
                    <Typography variant="subtitle2" className="article-publication"><Skeleton animation="wave" style={{ width: "25%" }}/></Typography>
                </Stack>
            </CardContent>

            <CardActions style={{ justifyContent: "space-between", height: "64px" }}>
                <Skeleton animation="wave" style={{ marginLeft: "10px", width: "15%", height: "60px" }}/>
                <Stack direction="row" spacing={1.5} style={{ marginRight: "3px" }}>
                    <Skeleton variant="circular">
                        <Avatar />
                    </Skeleton>

                    <Skeleton variant="circular">
                        <Avatar />
                    </Skeleton>
                </Stack>
            </CardActions>
        </Card>
    )
}

export default ArticleBoxSkeleton;