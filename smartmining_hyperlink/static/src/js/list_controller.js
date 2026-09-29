odoo.define('smartmining_hyperlink.list_controller', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var rpc = require('web.rpc');

    var JsTocallWizard = ListController.include({
        renderButtons: function($node){
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_button_to_call_wizard', function () {
                    var self = this;
                    var fields = [];
                    rpc.query({
                         model: 'smartmining.hyperlink',
                         method: 'login_smartmining',
                         args: [fields],
                    }).then(function(data){
                        console.log(data)
                        window.open('https://bomba.smartmining.cloud/Data/Dashboard/Index');
                    });
                });
                this.$buttons.appendTo($node);
            }
        },
    });
});