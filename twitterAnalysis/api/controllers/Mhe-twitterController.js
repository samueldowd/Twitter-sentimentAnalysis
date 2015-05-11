/**
 * Mhe-twitterController
 *
 * @description :: Server-side logic for managing mhe-twitters
 * @help        :: See http://links.sailsjs.org/docs/controllers
 */

module.exports = {
	
};

// a CREATE action
create: function(req, res, next) {

    var params = req.params.all();

    Sleep.create(params, function(err, tweet) {

        if (err) return next(err);

        res.status(201);

        res.json(tweet);

    });
}