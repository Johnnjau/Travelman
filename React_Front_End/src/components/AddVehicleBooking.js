import React, { useState } from 'react';
import { host_link } from '../data/rest_connection';

export const AddVehicleBooking = () => {
    const [dateQuery, setDateQuery] = useState('');
    const [timeFromQuery, setTimeFromQuery] = useState('');
    const [timeToQuery, setTimeToQuery] = useState('');
    const [firstNameQuery, setFirstNameQuery] = useState('');
    const [lastNameQuery, setLastNameQuery] = useState('');
    const [vehicleTypeQuery, setVehicleTypeQuery] = useState('');
    const [vehicleRegNumberQuery, setVehicleRegNumberQuery] = useState('');
    const [commentQuery, setCommentQuery] = useState('');
    const [message, setMessage] = useState('');
    const [isAccepted, setIsAccepted] = useState(false);

    const updateQuery = setQuery => event => {
        setQuery(event.target.value);
        setMessage('');
    };

    const handleSubmit = async () => {
        try {
            const response = await fetch(`${host_link}/add_vehicle_booking`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add Authorization if needed
                },
                body: JSON.stringify({
                    date: dateQuery,
                    time_from: timeFromQuery,
                    time_to: timeToQuery,
                    first_name: firstNameQuery,
                    last_name: lastNameQuery,
                    vehicle_type: vehicleTypeQuery,
                    vehicle_registration_number: vehicleRegNumberQuery,
                    comments: commentQuery,
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            setDateQuery('');
            setFirstNameQuery('');
            setLastNameQuery('');
            setVehicleTypeQuery('');
            setVehicleRegNumberQuery('');
            setCommentQuery('');
            setTimeFromQuery('');
            setTimeToQuery('');
            setIsAccepted(true);
            setMessage(data.message || 'Vehicle booking successful!');
        } catch (error) {
            setIsAccepted(false);
            setMessage(`Can’t access ${host_link}/add_vehicle_booking response. Error: ${error.message}`);
        }
    };

    return (
        <div className="add-vehicle">
            <div className="side-design">
                <div className="side-design-block"></div>
            </div>
            <div className="book-vehicle">
                <div className='book-vehicle-content'>
                    <div className="form-input">
                        <span className="form-input__label">FIRST NAME</span>
                        <input className='form-input__text' type="text" value={firstNameQuery} onChange={updateQuery(setFirstNameQuery)} />
                    </div>
                    <div className="form-input">
                        <span className="form-input__label">LAST NAME</span>
                        <input className='form-input__text' type="text" value={lastNameQuery} onChange={updateQuery(setLastNameQuery)} />
                    </div>
                </div>
                <div className='book-vehicle-content'>
                    <div className="form-input">
                        <span className="form-input__label">VEHICLE TYPE</span>
                        <input className='form-input__text' type="text" value={vehicleTypeQuery} onChange={updateQuery(setVehicleTypeQuery)} />
                    </div>
                    <div className="form-input">
                        <span className="form-input__label">VEHICLE REGISTRATION NUMBER</span>
                        <input className='form-input__text' type="text" value={vehicleRegNumberQuery} onChange={updateQuery(setVehicleRegNumberQuery)} />
                    </div>
                </div>
                <div className='book-vehicle-content'>
                    <div className="form-input">
                        <span className="form-input__label">DATE</span>
                        <input className="form-input__text" type="date" value={dateQuery} onChange={updateQuery(setDateQuery)} />
                    </div>
                </div>
                <div className='book-vehicle-content'>
                    <div className="form-input">
                        <span className="form-input__label">FROM</span>
                        <input className="form-input__text" type="time" value={timeFromQuery} onChange={updateQuery(setTimeFromQuery)} />
                    </div>
                    <div className="form-input">
                        <span className="form-input__label">TO</span>
                        <input className="form-input__text" type="time" value={timeToQuery} onChange={updateQuery(setTimeToQuery)} />
                    </div>
                </div>
                <div className="book-vehicle-content">
                    <div className="form-input">
                        <span className="form-input__label">COMMENTS</span>
                        <textarea className='form-input__text' value={commentQuery} onChange={updateQuery(setCommentQuery)} />
                    </div>
                </div>
                <div className="book-vehicle-content">
                    <button className="form-input__button" onClick={handleSubmit}>Book Vehicle</button>
                    <h3 className='form-input__message' style={isAccepted ? { color: "green" } : { color: "red" }}>{message}</h3>
                </div>
            </div>
        </div>
    );
};

export default AddVehicleBooking;
