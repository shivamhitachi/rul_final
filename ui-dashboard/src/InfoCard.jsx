/**
 * @file      : InfoCard.jsx
 * @summary   :
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-14
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : InfoCard
 */

import React from "react";
import PropTypes from 'prop-types';

export default class InfoCard extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div
                // className='text-color'
                style = {{
                    position        : 'absolute',
                    top             : this.props.top,
                    left            : this.props.left,
                    minWidth        : 250,
                    padding         : 10,
                    backgroundColor : 'white',
                    zIndex          : 500,
                    color           : '#656565',
                    textAlign       : 'left',
                    boxShadow       : '0 0 10px gray'
                }}
            >
                <div style = {{fontSize: 16}}>
                    {this.props.title}
                </div>
            </div>
        )
    }
}

InfoCard.propTypes = {
    top   : PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    left  : PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    title : PropTypes.string,
}

InfoCard.defaultProps = {
    top   : 50,
    left  : 50,
    title : 'Select something in USD Stage',
}
