import React, { Fragment, useState } from 'react';
import { img_home, img_add, img_search } from '../data/images';
import Background from './Background';
import AddVehicleBooking from './AddVehicleBooking';
import SearchContent from './SearchContent';
import { SideContent, SideContentButton } from './SideContent';
import { RecordsContent } from './RecordsContent';
import Header from './Header';
import { EditModal } from './EditModal';

function App() {

    const [isAddPane, setIsAddPane] = useState(false);
    const [isRecordsPane, setIsRecordsPane] = useState(true);
    const [isSearchPane, setIsSearchPane] = useState(false);
    const [header, setHeader] = useState('Vehicle Booking');
    const [subHeader, setSubHeader] = useState('TODAY');

    const updatePane = setPane => () => {
        setIsAddPane(false);
        setIsRecordsPane(false);
        setIsSearchPane(false);
        setPane(true);
    };

    const Pane = () => {
        if (isRecordsPane) {
            setHeader('Vehicle Booking');
            setSubHeader('Home');
            return (<RecordsContent />);
        }
        else if (isAddPane) {
            setHeader('Book a Vehicle');
            setSubHeader('Booking');
            return (<AddVehicleBooking />);
        }
        else if (isSearchPane) {
            setHeader('Search Record');
            setSubHeader('Date Range');
            return (<SearchContent />);
        }
    };

    return (
        <Fragment>
            <Background />
            <div className="app-body">
                <div className="main">
                    <Header header={header} sub_header={subHeader} />
                    <div className="content">
                        <SideContent>
                            <SideContentButton on_click={updatePane(setIsRecordsPane)} img_src={img_home} title='HOME' />
                            <SideContentButton on_click={updatePane(setIsAddPane)} img_src={img_add} title='ADD' />
                            <SideContentButton on_click={updatePane(setIsSearchPane)} img_src={img_search} title='SEARCH' />
                        </SideContent>
                        <Pane />
                    </div>
                </div>
            </div>
        </Fragment>
    );
}

export default App;
