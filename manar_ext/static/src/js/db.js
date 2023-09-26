odoo.define('manar_ext.DB', function (require) {
"use strict";
//var core = require('web.core');
/* The PosDB holds reference to data that is either
 * - static: does not change between pos reloads
 * - persistent : must stay between reloads ( orders )
 */
var PosDB = require('point_of_sale.DB');
PosDB.include({
	_partner_search_string: function(partner){
		var str = this._super(partner);
		//line break removed , space added
		str = str.replace(/(\r\n|\n|\r)/gm," ") + '\n';
		return str;
    },
});
});