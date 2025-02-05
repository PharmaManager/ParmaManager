paypal.buttons(
    
    {
        createOrder: function(data, actions) {
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: '10.0'
                    }
                }]
            });
        },
        onApprove: function(data, actions) {
            return   actions.order.capture().then(function(details) {

                alert('Transaction completed by ' + details.payer.name.given_name);

            });
        }

    }).render('#paypal-button-container');