Getting started
===============

This guide will show you how to use the library to create a simple XMPP client.


Creating a client
-----------------

First, you need to create a client instance:

.. code-block:: python

    from osmxmpp import XmppClient
    client = XmppClient("jabber.org", 5222)

The first argument is the hostname of the XMPP server, and the second argument is the port.

You can also specify the XMPP server hostname and port in the client instance like this:

.. code-block:: python

    client = XmppClient(host="jabber.org", port=5222)


Registering handlers
--------------------

After creating the client instance, you need to register handlers for the events you want to listen to.
For example, to listen to the ``ready`` event, you can use the ``on_ready`` method:

.. code-block:: python

    @client.on_ready
    def on_ready():
        print(f"Logged in as {client.jid}")

The ``on_ready`` method is a decorator that registers the ``on_ready`` handler.
The handler will be called when the client is ready to send and receive XMPP stanzas.

.. note::

    The ``on_ready`` will return immediately after registering the handler.
    It will not call handler immediately, but after event is triggered.

    You can still call the handler immediately by calling the ``on_ready`` method without the decorator:

    .. code-block:: python

        on_ready()


Sending a message
-----------------

To send a message, use the ``send_message`` method:

.. code-block:: python

    client.send_message("john@jabber.org", "Hello, John!")


Replying to a message
---------------------

To reply to a message, use the ``reply_to_message`` method:

.. code-block:: python

    client.reply_to_message("12345678", "john@jabber.org", "Thanks, John!")


Receiving a message
-------------------

To receive a message, you need to register a handler for the ``message`` event:

.. code-block:: python

    @client.on_message
    def on_message(message):
        if message.body is None: #Messages body can be empty
            return

        print(f"Received message from {message.from_jid}: {message.body}")
    

Features
--------

Features are used to implement specific XMPP stream features.
After connecting to the XMPP server, server will send a stream features stanza.

To connect features to the client, you need to call the ``connect_feature`` method before connecting to the XMPP server:

.. code-block:: python

    from osmxmpp.features.tls import TlsFeature

    client.connect_feature(
        TlsFeature(), 
        [
            XmppPermission.SEND_XML, 
            XmppPermission.RECV_XML, 
            XmppPermission.CHANGE_SOCKET, 
            XmppPermission.GET_SOCKET, 
            XmppPermission.OPEN_STREAM
        ]
    )
    # or
    client.connect_feature(
        TlsFeature(), 
        XmppPermission.ALL
    )

You can see the list of available features in the :doc:`features` section.


Extensions
----------

Extensions are used to implement specific XMPP extensions & etc.

To connect extensions to the client, you need to call the ``connect_extension`` method before connecting to the XMPP server:

.. code-block:: python

    from osmxmpp.extensions.omemo import OmemoExtension

    client.connect_extension(
        OmemoExtension(), 
        XmppPermission.ALL # or list of permissions
    )

You can see the list of available extensions in the :doc:`extensions` section.


Authentication
--------------

To authenticate to the XMPP server, you need to connect to the XMPP server with the ``SaslFeature``.
The ``SaslFeature`` will send the authentication request to the XMPP server.

To connect to the XMPP server with the ``SaslFeature``, you need to call the ``connect_feature`` method before connecting to the XMPP server:

.. code-block:: python

    from osmxmpp.features.sasl import SaslFeature, PlainMechanism

    client.connect_feature(
        SaslFeature(
            [
                PlainMechanism("john", "drowssap") # username and password
            ]
        ), 
        XmppPermission.ALL
    )

You can see the list of available authentication mechanisms in the :ref:`sasl` section.


Connecting to the XMPP server
------------------------------

To connect to the XMPP server, you need to call the ``connect`` method:

.. code-block:: python

    client.connect()

This will connect to the XMPP server and start the XMPP stream.

.. note::

    The ``connect`` method is synchronous, so it will block the execution of the program until the connection is ended.
    To add functionality to the program when it's connected, you can use handlers.


Example code
------------

Here is an example code that connects to the XMPP server, and listens to the ``/test`` command:

.. code-block:: python

    from osmxmpp import XmppClient, XmppPermission, XmppMessage
    from osmxmpp.features.tls import TlsFeature
    from osmxmpp.features.sasl import SaslFeature, PlainMechanism


    client = XmppClient("5222.de", 5222)

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
        TlsFeature(), 
        [
            XmppPermission.SEND_XML, 
            XmppPermission.RECV_XML, 
            XmppPermission.CHANGE_SOCKET, 
            XmppPermission.GET_SOCKET, 
            XmppPermission.OPEN_STREAM
        ]
    )

    client.connect_feature(
        SaslFeature(
            [
                PlainMechanism("john", "drowssap") # username and password
            ]
        ), 
        XmppPermission.ALL
    )

    client.connect_feature(
        BindFeature(
            "osmxmpp" # resource
        ), 
        XmppPermission.ALL
    )

    try:
        client.connect()
    except KeyboardInterrupt:
        client.disconnect()