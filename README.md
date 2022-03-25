# OSSLSelection
A tool for selecting open source licenses for projects. Open source license compatibility, individual open source style, business model, community development, terms details, popularity, readability and other factors are considered  
# 介绍
一种开源许可证选择工具，从开源许可证兼容性检测、开源许可证类型指导、开源许可证条款细节分析对比、使用流行度、可读性等方面因素指导开发者为项目选择开源许可证，使用Django+jQuery实现。
# 环境配置
- 操作系统：windows
- 运行环境：python3.6+、perl5、JDK8、vs2005
- 第三方工具部署：
   1. 下载许可证识别工具Ninka(<https://github.com/dmgerman/ninka>)并解压，将ninka-master\lib中的文件复制到C:\Strawberry\perl\lib，将ninka-master\bin中的文件复制到C:\Strawberry\perl\bin，ninka-master\comments文件夹复制到制到C:\Strawberry\perl\，cd到comments\，执行nmake；测试：cd到perl\bin\，执行perl ninka [filename]，查看是否filename的许可信息。
   2. 下载静态依赖识别工具depends的release版(<https://github.com/multilang-depends/depends/releases/>)并解压，cd到depends-0.9.6-package\depends-0.9.6，执行java -jar depends.jar <lang> <src_path> <output_file>，查看是否成功输出.
