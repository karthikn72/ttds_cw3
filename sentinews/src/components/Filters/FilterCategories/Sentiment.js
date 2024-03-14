import React from 'react';
import { Collapse, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Checkbox, Divider } from '@mui/material';
import FilterTitle from '../FilterTitle';

function Sentiment({updatePage, expand, handleExpand, sentimentsAvailable}) {

    const updateFilter = (value) => () => {
        updatePage("add", ["", "sentiment", value]);
    }

    return(
        <div>
            <FilterTitle name={`SENTIMENT (${sentimentsAvailable.length})`} expand={expand} handleExpand={handleExpand}/>
            <Divider/>
            <Collapse in={expand} timeout="auto" unmountOnExit style={{ height: "auto", overflow: "auto", backgroundColor: "#F5F5F5" }}>
                <List sx={{ width: '100%' }}>
                    {sentimentsAvailable.map((value) => {
                        const labelId = `checkbox-${value}`;
                        return (
                            <ListItem key={value} disablePadding>
                                <ListItemButton role={undefined} onClick={updateFilter(value)} dense>
                                    <ListItemIcon>
                                        <Checkbox edge="start" tabIndex={-1} disableRipple inputProps={{ 'aria-labelledby': labelId }}/>
                                    </ListItemIcon>
                                    <ListItemText id={labelId} primary={value} />
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>
            </Collapse>
            <Divider/>
        </div>
    )
}

export default Sentiment;