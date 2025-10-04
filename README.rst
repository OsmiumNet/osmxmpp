OsmXMPP
=======

Python XMPP library


Installing
----------

**Python 3.10 or higher is required.**

To install the library you can just run the following command:

.. note::

    A `Virtual Environment <https://docs.python.org/3/library/venv.html>`__ is recommended to install
    the library, especially on Linux where the system Python is externally managed and restricts which
    packages you can install on it.


.. code:: sh

    # Linux/macOS
    python3 -m pip install -U osmxmpp

    # Windows
    py -3 -m pip install -U osmxmpp


Quick Example
--------------

.. code:: py

    from osmxmpp.client import XmppClient
    from osmxmpp.permission import XmppPermission
    from osmxmpp.message import XmppMessage
    from osmxmpp.features.tls import TlsFeature
    from osmxmpp.features.sasl import SaslFeature, PlainMechanism

    import certifi


    client = XmppClient("jabber.org", port=5222)

    @client.on_disconnect
    def on_disconnect():
        print("Disconnected from the XMPP server")

    @client.on_ready
    def on_ready():
        print(f"Logged in as {client.jid}")

    @client.on_message
    def on_message(message):
        if message.body is None: #Messages body can be empty
            return

        if message.body == "/test":
            client.send_message(message.from_jid, "Hello!")

    client.connect_feature(
        TlsFeature(
            verify_locations=certifi.where()
        ),
        TlsFeature.REQUIRED_PERMISSIONS
    )

    client.connect_feature(
        SaslFeature(
            [
                PlainMechanism("john", "drowssap") # username and password
            ]
        ),
        SaslFeature.REQUIRED_PERMISSIONS
    )

    client.connect_feature(
        BindFeature(
            "osmxmpp" # resource
        ),
        BindFeature.REQUIRED_PERMISSIONS
    )

    try:
        client.connect()
    except KeyboardInterrupt:
        client.disconnect()

Links
------

- `Documentation <https://osmxmpp.readthedocs.io/en/latest/>`_