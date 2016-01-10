工程的启动（Xcode环境下）：
1.双击ExtraEyetrackerDataFeature.xcodeproj在Xcode下打开工程
2.本工程依赖了Opencv的cv::Directory类来获取一个文件夹下的文件名list，所以首先要进行opencv的配置，在Xcode中配置依赖libopencv_contirb.2.4.x.dylib（本人使用的opencv版本为2.4.9）

本工程解决两个问题，一个是主观评分的归类，可以将每个人对每幅图像的评分整理归档为csv文件。
具体的：subjectscorefilename赋值为从众包网站上下载的文件路径；
函数writeDataToFile中传入处理后文件的保存路径。

第二，眼动过程分离与滤波，将带有眨眼过程的眼动数据进行滤波与眼动过程分离，最后的结果以csv的形式保存。

另外的一个重点是：眼动过程分离时涉及到了主辅眼的，因此，在开始执行时需要指定滤波的参考眼睛为何。

具体的：
1、在dir.GetListFiles()处插入眼动数据文件所在文件夹名称
2、在创建智能指针m_eyetrackerdatareader时指定左眼还是右眼。
3、在writeDataToFile（）处修改要保存眼动数据的文件夹名称。
