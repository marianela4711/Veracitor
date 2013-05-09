/**
    Displays information about a specific Producer, User or Information ob-
    ject in the database. Visualizes a portion of the system database via the
    WebUI.NetworkView.Visualizer.

    The view is divided into two distinct areas. One area contains detailed
    information about the selected source node. The other area contains a
    visualization of a portion of the database relative to the source node, as
    well as tools to alter the visualization of the network.
    @constructor
 */
var NetworkController = function (controller) {

    var network_controller = this;
    var visualizer = new Visualizer(network_controller);
    var network_info;

    var selected_producer = null;
    var user;

    /**
       This function is called by the super controller when the tab is opened.
     */
    this.on_tab_active = function () {

    };

    /**
       Initialize variables and events.
     */
    var initialize = function () {
        network_info = $('#network-graph > .info');

        display_network_information('Use the search to find producers and information.');

        $.post('/utils/get_user', {
            'user_name': vera.user_name
        }, function(data){
            user = data;
        });


        $('#add-to-group').click(function(evt) {
            $.post('/jobs/network/add_to_group', {
                'group_name': $('#group_name').val(),
                'producer': $('h1.title').text()
            }, function(data) {
                // TODO: display success/fail
                console.log(data);
            });
        });

        $('#network_rate_producer > .button').click(function ( evt ) {
            var rating = $('#network_rate_producer > .rating > option:selected').html();

            $.post('/jobs/network/rate/producer', {
                'source': vera.user_name,
                'target': selected_producer.name,
                'tag': $('#rate-producer-tag').val(),
                'rating': rating,
            }, function ( data ) {
                // TODO: show success/fail
                visualizer.fetch_neighbors(data.source.name, (function ( target ) {
                    return function () {
                        network_controller.visualize_producer_in_network(target);
                    };
                })(data.target.name));
            })
                .fail(function ( data ) {
                    // TODO
                });
        });

        $('#compute-trust').click( function(evt){
            request_tidaltrust_value(vera.user_name,
                                     selected_producer.name,
                                     $("#compute-trust-tag").val());
        });

        /**
         * Toggle tip-text when clicking question mark icons. Needs the structure of the
         * dom to be like this:
         *
         * <p>
         *   text <infobutton>
         * </p>
         * <div tip-text></div>
         */
        $('.network-info-piece span.question-mark').click(function(evt){
            $(this).parent().next().toggle();
        });
    };

    /**
       Request a TidalTrust value.
    */
    function request_tidaltrust_value(source, sink, tag) {
        console.log(source +" "+ sink +" " + tag);
        $.post('/jobs/algorithms/tidal_trust', {
            'source': source,
            'sink': sink,
            'tag': tag
        }, function (data) {
            var job_id = data['job_id'];

            controller.set_job_callback(job_id, function (data) {
                // TODO: display success/fail
                console.log(data);
                $('#network-compute-trust .feedback #trust-result').html(data.result.trust);
                $('#network-compute-trust .feedback #trust-result-threshold').html(data.result.threshold);
                $('#network-compute-trust .feedback').toggle();
            });
        })
        .fail(function () {
            $('#search-result').html('<h2>Server error.</h2>');
        });
    }

    /**
        Creates an interactive visualization network of the trust ratings
        directly or indirectly associated with the given Producer (source
        node) within the GlobalNetwork. Only nodes that have a trust
        relation with the source node at a maximum of depth nodes away
        from the source node will be visualized. If -1 is input as depth
        there will be no restrictions as to how close a node has to be to
        the source node in order to be part of the visualization (that is the
        entire network will be visualized).
     */
    this.visualize_producer_in_network = function (prod) {
        $.post('/jobs/network/path', {
            'source': vera.user_name,
            'target': prod
        }, function (data) {
            network_controller.display_producer_information(data.path.target);

            if (data.path.nodes.length > 0) {
                hide_network_information();

                selected_producer = data.path.source;

                visualizer.visualize_path_in_network(data.path.source.name,
                                                     data.path.target.name,
                                                     data.path.nodes,
                                                     data.path.ghosts);
            } else {
                display_network_information('No path found');
            }
        }).fail(function (data) {
            // TODO: display fail
        });
    };

    /**
       Displays information about the given producer.
     */
    this.display_producer_information = function (prod) {
        // A reference to this controller
        var network_controller = this;

        selected_producer = prod;

        $('#network-info-view .title').html(prod.name);
        $('#network-info-view .description').html(prod.description);
        $('#network-info-view .url').html($('<a>').attr('href', prod.url).html(prod.url));
        $('#network-info-view .type').html(prod.type_of);

        var ul = $('<ul>');
        for (var i in prod.infos) {
            ul.append($('<li>')
                      .append($('<p>').html(prod.infos[i].title))
                      .append($('<a>').attr('href', prod.infos[i].url).html(prod.infos[i].url))
                      .append(get_rating_dropdown_html())
                      .append($('<input>').attr({
                          'type': 'button',
                          'value': 'Rate information'
                      }).click((function ( url ) {
                          return function ( evt ) {
                              var rating = $(this).parent().find(':selected').html();
                              rate_information(url, rating);
                          };
                      })(prod.infos[i].url))));
        }
        $('#network-info-view .informations').html(ul);
    };

    var rate_information = function ( url, rating ) {
        $.post('/jobs/network/rate/information', {
            'prod': vera.user_name,
            'url': url,
            'rating': rating
        }, function (data) {
            // TODO: display success/fail
        }).fail(function (data) {
            // TODO: display fail
        });
    };

    var get_rating_dropdown_html = function () {
        var select = $('<select>').addClass('rating');

        for (var i = 1; i <= 5; i += 1) {
            select.append($('<option>').attr('value', i).html(i));
        }

        return select;
    };

    /**
        Visualizes the given trust network.
     */
    this.visualize_trust_network = function (network) {
        visualizer.visualize_trust_network(network);
    };

    var display_network_information = function ( info ) {
        network_info.css('display', 'block');
        network_info.find('.content').html($('<p>').html(info));

        try {
            visualizer.clear_graph();
        } catch (exc) {
            // cytoscape has not yet loaded
        }
    };

    var hide_network_information = function () {
        network_info.css('display', 'none');
    };

    // Initialize this controller
    initialize();

}
