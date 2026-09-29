odoo.define('smartmining_hyperlink.odoo_tutorial', function(require) {
    'use strict'

    console.log('popup.js loaded')
    var FormController = require('web.FormController');
    var rpc = require('web.rpc');

    var ExtendFromController = FormController.include({
        saveRecord: function () {
            console.log('saveRecord')
            var res = this._super.apply(this, arguments);
            if (this.modelName == 'smartmining.hyperlink'){
                this.do_notify('success', 'Record Saved');
                var self = this
                self._rpc({
                    model: 'smartmining.hyperlink',
                    method: 'search_read',
                    fields: ['token'],
                    context: self.context
                }). then(function(result){
                    console.log(result)
                });

                var fields = []
                rpc.query({
                     model: 'smartmining.hyperlink',
                     method: 'login_smartmining',
                     args: [fields],
                }).then(function(data){
//                    window.open('https://bomba.smartmining.cloud/Data/Dashboard/Index');
                });

            }
            return res;
        }
    });
});