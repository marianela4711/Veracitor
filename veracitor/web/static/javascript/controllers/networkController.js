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

    var visualizer = new Visualizer(this);

    /**
       This function is called by the super controller when the tab is opened.
     */
    this.on_tab_active = function () {

    };

    /**
       Request a SUNNY value.
    */
    function request_sunny_value(source, sink, tag) {
         $.post('/jobs/algorithms/tidal_trust', {
            'source': source,
            'sink': sink,
            'tag': tag
        }, function (data) {
            var job_id = data['job_id'];

            controller.set_job_callback(job_id, function (data) {
                console.log(data.result);

                $('#calculated-trust').html(data.result.trust);
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
    this.visualize_producer_in_network = function (prod, depth) {
        var network_controller = this;

        $.post('/jobs/network/path', {
            'source': session.user.name,
            'target': prod.name
        }, function (data) {
            network_controller.display_producer_information(prod);

            console.log(data);

            visualizer.visualize_producer_in_network(prod, data.path.nodes, depth);
        }).fail(function (data) {
            console.log(data);
        });

        /*
        $.post('/jobs/network/neighbors', {
            'name': session.user.name,
            'depth': depth
        }, function (data) {
            network_controller.display_producer_information(prod);

            console.log(data);

            visualizer.visualize_producer_in_network(prod, data.neighbors, depth);
        }).fail(function (data) {
            console.log(data);
        });
        */
    };

    /**
       Displays information about the given producer.
     */
    this.display_producer_information = function (prod) {
        $('#network-info-view .title').html(prod.name);
        $('#network-info-view .description').html(prod.description);
        $('#network-info-view .url').html($('<a>').attr('href', prod.url).html(prod.url));
        $('#network-info-view .type').html(prod.type_of);
    };

    /**
        Visualizes the given trust network.
     */
    this.visualize_trust_network = function (network) {
        visualizer.visualize_trust_network(network);
    };

}
