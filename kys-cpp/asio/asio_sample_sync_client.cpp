#include <iostream>
#include <vector>
#include <asio.hpp>

// _WIN32_WINNT=0x0A00

using asio::ip::tcp;

int main(int argc, char* argv[])
{
    try
    {
        asio::io_context io_context;

        tcp::resolver resolver(io_context);
        tcp::resolver::results_type endpoints =
            resolver.resolve("localhost", "daytime");

        tcp::socket socket(io_context);
        asio::connect(socket, endpoints);

        for (;;)
        {
            std::vector<char> buf(128);
            asio::error_code error;
            // MSG_WAITALL(or whatever) read until buffer is full
            // asio::read(socket, asio::buffer(buf));
            size_t len = socket.read_some(asio::buffer(buf), error);

            if (error == asio::error::eof)
                break; // Connection closed cleanly by peer.
            else if (error)
                throw asio::system_error(error); // Some other error.

            std::cout.write(buf.data(), len);
        }
    }
    catch (std::exception& e)
    {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}