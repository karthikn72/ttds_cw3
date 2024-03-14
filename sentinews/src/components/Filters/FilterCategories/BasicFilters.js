import React from 'react';
import { List, ListItem, ListItemButton, ListItemIcon, ListItemText, Checkbox, Stack, ListSubheader, useTheme, useMediaQuery } from '@mui/material';
import { DateRange } from 'react-date-range';

function BasicFilters({checked, dateRange, setChecked, setDateRange}) {

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    const handleSentiments = (value) => () => {
        const currentIndex = checked.indexOf(value);
        const newChecked = [...checked];
    
        if (currentIndex === -1) {
          newChecked.push(value);
        } else {
          newChecked.splice(currentIndex, 1);
        }
    
        setChecked(newChecked); 
    };

    return(
        <div>
            <Stack spacing={0} direction={ isMobile ? "column" : "row" }>
                <List sx={{ width: '100%', height: "420px", textAlign: "center" }} subheader={<ListSubheader>Date Range</ListSubheader>}>
                    <DateRange style={{ width: "320px" }} editableDateInputs={true} onChange={item => setDateRange([item.selection])} ranges={dateRange}/>
                </List>

                <List sx={{ width: '100%', alignItems: "center", textAlign: "center" }} subheader={<ListSubheader>Sentiments</ListSubheader>}>
                    {["Positive", "Neutral", "Negative"].map((value) => {
                        const labelId = `checkbox-${value}`;
                        return (
                            <ListItem key={value}>
                                <ListItemButton role={undefined} onClick={handleSentiments(value)} dense>
                                    <ListItemIcon>
                                        <Checkbox edge="start" checked={checked.indexOf(value) !== -1}  tabIndex={-1} disableRipple inputProps={{ 'aria-labelledby': labelId }}/>
                                    </ListItemIcon>
                                    <ListItemText id={labelId} primary={value} />
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>
            </Stack>
        </div>
    )
}

export default BasicFilters;