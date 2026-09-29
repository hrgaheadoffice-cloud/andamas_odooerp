odoo.define('smartmining_hyperlink.button', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc');
    var link;

    var TreeButton = ListController.extend({
       buttons_template: 'smartmining_hyperlink.buttons',
       events: _.extend({}, ListController.prototype.events, {
           'click .open_wizard_action': '_OpenWizard',
       }),
       _OpenWizard: function () {
            var args = []

            rpc.query({
                 model: 'smartmining.hyperlink',
                 method: 'get_link',
                 args: [args],
            }).then(function(res){
                link = res;
            });

            rpc.query({
                 model: 'smartmining.hyperlink',
                 method: 'get_user_data',
                 args: [args],
            }).then(function(data){
                window.open(link + '/Authentication/Login/OdooIndex?data=' + data);
            });

       }
    });
    var TreeView = ListView.extend({
       config: _.extend({}, ListView.prototype.config, {
           Controller: TreeButton,
       }),
    });
    viewRegistry.add('button', TreeView);
});