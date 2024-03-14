import React from 'react';
import { Divider, Tooltip, List, ListItem, Collapse, Chip, IconButton } from '@mui/material';
import { ClearSharp } from '@mui/icons-material';
import { format } from 'date-fns/format';

function CurrentFilters({updatePage, dateRangeApplied, sentimentsApplied, authorsApplied, categoriesApplied, publicationsApplied}) {

    const formatDateRange = (fromString, toString) => { 
        const stringFormat = 'dd MMM yyyy';
        const from = format(new Date(fromString), stringFormat);
        const to = format(new Date(toString), stringFormat);
        return `${from} - ${to}`;
    };

    const filters = [
        ...(dateRangeApplied.length > 0 ? [{ source: "date", key: "date", label: `${formatDateRange(dateRangeApplied[0],dateRangeApplied[1])}` }] : []),
        ...sentimentsApplied.map(sentiment => ({ source: "sentiment", key: sentiment, label: `Sentiment: ${sentiment}` })),
        ...authorsApplied.map(author => ({ source: "author", key: author, label : `Author: ${author}` })),
        ...categoriesApplied.map(category => ({ source: "category", key: category, label: `Category: ${category}` })),
        ...publicationsApplied.map(publication => ({ source: "publication", key: publication, label: `Publication: ${publication}` }))
    ]

    function clearAllFilters() {
        updatePage("remove", ["all", "", ""]);
    }

    const deleteFilter = (source, value) => {
        updatePage("remove", ["single", source, value]);
    }

    return(
        <div>
            <div className='icon-segment' style={{ height: "60px" }}>
                <h6 className='filter-title'>CURRENT FILTERS ({filters.length})</h6>
                <Tooltip title="Clear All Filters" placement='top'>
                    <IconButton onClick={clearAllFilters} className='filter-icon'>
                        <ClearSharp/> 
                    </IconButton>
                </Tooltip>
            </div>
            <Divider/>
            <Collapse in={true} timeout="auto" style={{ height: "auto", overflow: "auto", backgroundColor: "#F5F5F5" }}>
                <List sx={{ width: '100%' }}>
                    {filters.map((data) => {
                        return (
                            <ListItem key={data.key}>
                                <Chip label={data.label} onDelete={() => deleteFilter(data.source, data.key)} />
                            </ListItem>
                        )
                    })}
                </List>
            </Collapse>
            <Divider/>
        </div>
    )
}

export default CurrentFilters;