#include <ctime>
#include <iostream>
#include <string>
#include <asio.hpp>
#include <thread>
#include <chrono>

// _WIN32_WINNT=0x0A00

using asio::ip::tcp;
#pragma warning(disable : 4996)

std::string make_daytime_string()
{
    std::chrono::system_clock::time_point p = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(p);
    return std::ctime(&t);
}

int main()
{
    try
    {
        asio::io_context io_context;
        tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 13));
        tcp::socket socket(io_context);
        acceptor.accept(socket);
        for (;;)
        {
            std::string message = make_daytime_string();
            asio::error_code ignored_error;
            asio::write(socket, asio::buffer(message), ignored_error);
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
    catch (std::exception& e)
    {
        std::cerr << e.what() << std::endl;
    }
    return 0;
}